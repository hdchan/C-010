import dash_ag_grid as dag
from dash import Dash, html, dcc, Input, Output, ClientsideFunction, State, clientside_callback, callback
from dash_iconify import DashIconify
import random
import json
app = Dash()

left_data = [
    {
        'henry': i + 100,
        'color': 'Blue',
        'value1': random.randint(1, 100),
        'value2': random.randint(1, 100),
    } for i in range(5)
]

right_data = [
    {
        'henry': i + 200,
        'color': 'Green',
        'value1': random.randint(1, 100),
        'value2': random.randint(1, 100),
    } for i in range(5)
]


def init_grid(side):
    columnDefs = [
        {'field': 'henry', "checkboxSelection": True, "headerCheckboxSelection": True},
        {'field': 'color'},
        {'field': 'value1'},
        {'field': 'value2'},
    ]

    return dag.AgGrid(
        id=f'row-dragging-grid2grid-complex-{side}',
        rowData=left_data if side == 'left' else right_data,
        columnDefs=columnDefs,
        defaultColDef={'resizable': True},
        columnSize="sizeToFit",
        dashGridOptions={
            "rowDragManaged": True,
            "rowDragEntireRow": True,
            "rowDragMultiRow": True, "rowSelection": "multiple",
            "suppressMoveWhenRowDragging": True
        },
        rowClassRules={
            "grid-green-row": 'params.data.color == "Green"',
            "grid-blue-row": 'params.data.color == "Blue"',
        },
        getRowId="params.data.henry",
    )


app.layout = html.Div(
    [
        html.Button('Reset', id='btn-row-dragging-grid2grid-complex-reset'),
        dcc.RadioItems(
            id='radio-row-dragging-grid2grid-complex-option',
            options={
                'move': 'Move',
                'deselect': 'Copy and Deselect',
                'none': 'Copy and Keep Selected'
            },
            value='move', inline=True, style={'margin': 10}
        ),
        html.Div(
            [
                init_grid('left'),
                html.Div(
                    DashIconify(icon="fa6-regular:trash-can", width=30),
                    id='div-row-dragging-grid2grid-complex-bin'
                ),
                init_grid('right'),
            ], className='row-dragging-grid-to-grid-container',
        ),
        html.Pre(id="pre-cell-selection-simple-click-callback")
    ]
)

@callback(
    Output("pre-cell-selection-simple-click-callback", "children"),
    Input("row-dragging-grid2grid-complex-left", "modelUpdated")
)
def display_cell_clicked_on(test):
    print('test')
    # return f"Clicked on cell:\n{json.dumps(cell, indent=2)}" if cell else "Click on a cell"

clientside_callback(
    ClientsideFunction('addDropZone', 'dropZoneGrid2GridComplex'),
    Output('row-dragging-grid2grid-complex-left', 'id'),
    Input('radio-row-dragging-grid2grid-complex-option', 'value'),
    State('row-dragging-grid2grid-complex-left', 'id'),
    State('row-dragging-grid2grid-complex-right', 'id'),
)


@callback(
    Output("row-dragging-grid2grid-complex-left", "rowData"),
    Output("row-dragging-grid2grid-complex-right", "rowData"),
    Input("btn-row-dragging-grid2grid-complex-reset", "n_clicks"),
    prevent_initial_call=True,
)
def reset_rows(_):
    return left_data, right_data


if __name__ == "__main__":
    app.run(debug=True)
