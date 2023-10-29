import Example from "./Navbar";
import Graphviz from "graphviz-react";
import { useContext } from 'react';
import { GraphContext } from './GraphContext';

export default function AST(){
    const { graphCode } = useContext(GraphContext);
    return (
        <div className="h-screen bg-gray-800">
        <Example/>
        <Graphviz dot = {graphCode ? graphCode : `digraph{ nodoinicial[label="No hay valores"]}`} />
        </div>
    );
}