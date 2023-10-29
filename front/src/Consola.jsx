import React from 'react'
import CodeMirror from "@uiw/react-codemirror";

export default function Consola(props) {
  return (
    <CodeMirror
      className="scrollbar-track-gray-300 scrollbar-thumb-gray-500 scrollbar-thin rounded-md"
      height="590px"
      value={props.consola}
      theme="dark"
    />
  );
}

