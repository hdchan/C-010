window.dash_clientside = window.dash_clientside || {};

window.dash_clientside.addDropZone = {
    dropZoneGrid2GridComplex: async function (dropOption, gridIdLeft, gridIdRight) {

        // Get the grids APIs
        const gridLeftAPI = await dash_ag_grid.getApiAsync(gridIdLeft);
        const gridRightAPI = await dash_ag_grid.getApiAsync(gridIdRight);

        const addBinDropZone = sourceGridAPI => {

            const binContainer = document.querySelector('#div-row-dragging-grid2grid-complex-bin');

            const binDropZoneParams = {
                getContainer: () => binContainer,

                onDragEnter: params => {
                    binContainer.style.color = '#e78ac3';
                    binContainer.style.transform = 'scale(1.5)';
                },

                onDragLeave: params => {
                    binContainer.style.color = null;
                    binContainer.style.transform = 'scale(1)';
                },

                onDragStop: params => {
                    binContainer.style.color = null;
                    binContainer.style.transform = 'scale(1)';
                    console.log(sourceGridAPI.getState())
                    // Remove dragged rows from the Source Grid
                    sourceGridAPI.applyTransaction({
                        remove: params.nodes.map(node => node.data)
                    });
                },
            }

            sourceGridAPI.addRowDropZone(binDropZoneParams);

        };

        addBinDropZone(gridLeftAPI)
        addBinDropZone(gridRightAPI)

        const addGridDropZone = (sourceGridAPI, targetGridAPI) => {

            const gridDropZoneParams = {
                onDragStop: params => {
                    console.log(sourceGridAPI.getState())
                    if (dropOption === 'move') {
                        // Remove dragged rows from the Source Grid
                        sourceGridAPI.applyTransaction({
                            remove: params.nodes.map(node => node.data)
                        });
                    } else if (dropOption === 'deselect') {
                        // Only deselect all rows
                        sourceGridAPI.deselectAll();
                    }
                },
            }

            const gridDropZone = targetGridAPI.getRowDropZoneParams(gridDropZoneParams);
            // Remove existing gridDropZone before adding the updated one depending on the dropOption
            sourceGridAPI.removeRowDropZone(gridDropZone);
            sourceGridAPI.addRowDropZone(gridDropZone);

        };

        addGridDropZone(gridLeftAPI, gridRightAPI)
        addGridDropZone(gridRightAPI, gridLeftAPI)

        return window.dash_clientside.no_update
    },
}