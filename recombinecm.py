"""Contents manager which splits a 'clean' copy out and recombines on load.
"""

__version__ = '0.1'

from copy import deepcopy
import difflib
import os.path

from notebook.services.contents.filemanager import FileContentsManager
from notebook.services.contents.filecheckpoints import FileCheckpoints

def clean_copy(nb):
    nb2 = deepcopy(nb)

    for cell in nb2.cells:
        if cell.cell_type == 'code':
            cell.outputs = []
            cell.execution_count = None

    return nb2

def junkfunc(source):
    # Ignore empty cells for the sequence matching
    return not source.strip()

def recombine(clean, with_outputs):
    clean_code_cells, clean_code_ixs = [], []
    for i, cell in enumerate(clean.cells):
        if cell.cell_type == 'code':
            clean_code_cells.append(cell.source)
            clean_code_ixs.append(i)

    dirty_code_cells, dirty_code_ixs = [], []
    for i, cell in enumerate(with_outputs.cells):
        if cell.cell_type == 'code':
            dirty_code_cells.append(cell.source)
            dirty_code_ixs.append(i)

    result = deepcopy(clean)

    sm = difflib.SequenceMatcher(junkfunc, clean_code_cells, dirty_code_cells)

    for match in sm.get_matching_blocks():
        for i in range(match.size):
            target_cell = result.cells[clean_code_ixs[match.a + i]]
            source_cell = with_outputs.cells[dirty_code_ixs[match.b + i]]
            target_cell.outputs = source_cell.outputs
            target_cell.execution_count = source_cell.execution_count

    return result

class RecombineContentsManager(FileContentsManager):

    def _save_notebook(self, os_path, nb):
        super()._save_notebook(os_path, nb)

        # Create another file with the clean copy of the notebook
        nb2 = clean_copy(nb)

        super()._save_notebook(os_path + '.clean', nb2)

    def _read_notebook(self, os_path, as_version=4):
        with_output = super()._read_notebook(os_path, as_version)
        try:
            clean = super()._read_notebook(os_path + '.clean', as_version)
        except FileNotFoundError:
            # We didn't save this file, so just return the regular notebook
            return with_output

        return recombine(clean, with_output)

    def _checkpoints_class_default(self):
        return RecoFileCheckpoints

class RecoFileCheckpoints(FileCheckpoints):
    def restore_checkpoint(self, contents_mgr, checkpoint_id, path):
        super().restore_checkpoint(contents_mgr, checkpoint_id, path)

        # Delete the .clean version of the file, so we don't try to recombine
        # it with the checkpointed copy
        clean_path = contents_mgr._get_os_path(path) + '.clean'
        if os.path.isfile(clean_path):
            os.unlink(clean_path)
