from nbformat.v4 import new_notebook, new_code_cell, new_output, new_markdown_cell

import recombinecm

w_output_1 = new_notebook(cells = [
    new_code_cell("print('foo')",
                  execution_count=1,
                  outputs = [
                      new_output('stream', text='foo\n'),
                  ]),
    new_markdown_cell('This is some *markdown*'),
    new_code_cell("a=1\na",
                  execution_count=2,
                  outputs = [
                      new_output('execute_result',
                                 {'text/plain': '1'},
                                 execution_count=1)
                  ]),
    new_code_cell("print('fob')",
                  execution_count=4,
                  outputs = [
                      new_output('stream', text='fob\n'),
                  ]),
])

clean_1 = new_notebook(cells = [
    new_code_cell("print('foo')"),
    new_markdown_cell('This is some *markdown*'),
    new_code_cell("a=1\na"),
    new_code_cell("print('fob')"),
])

w_output_1_extra_cells = new_notebook(cells = [
    new_code_cell("print('foo')",
                  execution_count=1,
                  outputs = [
                      new_output('stream', text='foo\n'),
                  ]),
    new_markdown_cell('This is some *markdown*'),
    new_code_cell("sys.stdout.write('qrx')",
                  execution_count=3,
                  outputs = [
                      new_output('stream', text='qrx')
                  ]),
    new_markdown_cell('More text that should be ignored'),
    new_code_cell("a=1\na",
                  execution_count=2,
                  outputs = [
                      new_output('execute_result',
                                 {'text/plain': '1'},
                                 execution_count=1)
                  ]),
    new_code_cell("print('fob')",
                  execution_count=4,
                  outputs = [
                      new_output('stream', text='fob\n'),
                  ]),
])

clean_1_extra_cells = new_notebook(cells = [
    new_code_cell("print('foo')"),
    new_markdown_cell('This is some *markdown*'),
    new_code_cell("sys.stdout.write('qrx')"),
    new_markdown_cell('More text that should be ignored'),
    new_code_cell("a=1\na"),
    new_code_cell("print('fob')"),
])

clean_1_cells_removed = new_notebook(cells = [
    new_markdown_cell('This is some *markdown*'),
    new_code_cell("print('fob')"),
])

def test_clean_basic():
    res = recombinecm.clean_copy(w_output_1)

    c = res.cells
    assert c[0].cell_type == 'code'
    assert c[0].outputs == []
    assert c[0].execution_count == None

    assert c[1].cell_type == 'markdown'

    assert c[2].cell_type == 'code'
    assert c[2].outputs == []
    assert c[2].execution_count == None

    # Check that we didn't modify the original
    assert w_output_1.cells[0].outputs != []

def test_recombine_basic():
    res = recombinecm.recombine(clean_1, w_output_1)

    c = res.cells
    assert c[0].cell_type == 'code'
    assert len(c[0].outputs)
    assert c[0].outputs[0].output_type == 'stream'
    assert c[0].execution_count == 1

    assert c[1].cell_type == 'markdown'

    assert c[2].cell_type == 'code'
    assert len(c[2].outputs) == 1
    assert c[2].outputs[0].output_type == 'execute_result'
    assert c[2].execution_count == 2

    assert c[3].cell_type == 'code'
    assert c[3].outputs[0].text == 'fob\n'

    # Check that this is a separate object
    assert res is not w_output_1
    assert res is not clean_1
    assert clean_1.cells[0].outputs == []

def test_recombine_extra_locally():
    res = recombinecm.recombine(clean_1, w_output_1_extra_cells)

    c = res.cells
    assert c[0].cell_type == 'code'
    assert len(c[0].outputs)
    assert c[0].outputs[0].output_type == 'stream'
    assert c[0].execution_count == 1

    assert c[1].cell_type == 'markdown'

    assert c[2].cell_type == 'code'
    assert len(c[2].outputs) == 1
    assert c[2].outputs[0].output_type == 'execute_result'
    assert c[2].execution_count == 2

    assert c[3].cell_type == 'code'
    assert c[3].outputs[0].text == 'fob\n'

def test_recombine_extra_in_clean():
    res = recombinecm.recombine(clean_1_extra_cells, w_output_1)

    c = res.cells
    assert c[0].cell_type == 'code'
    assert len(c[0].outputs)
    assert c[0].outputs[0].output_type == 'stream'
    assert c[0].execution_count == 1

    assert c[1].cell_type == 'markdown'

    assert c[4].cell_type == 'code'
    assert len(c[4].outputs) == 1
    assert c[4].outputs[0].output_type == 'execute_result'
    assert c[4].execution_count == 2

    assert c[5].cell_type == 'code'
    assert c[5].outputs[0].text == 'fob\n'

    # This shouldn't match anything in the local version
    assert c[2].cell_type == 'code'
    assert c[2].outputs == []

def test_recombine_clean_reduced():
    res = recombinecm.recombine(clean_1_cells_removed, w_output_1)
    c = res.cells

    assert c[0].cell_type == 'markdown'

    assert c[1].cell_type == 'code'
    assert c[1].outputs[0].text == 'fob\n'
