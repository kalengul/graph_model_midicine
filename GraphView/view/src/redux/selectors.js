export const selectNodeById = (state, id) => {
    return state.graph.schema.nodes.find(node => node.id === id);
};