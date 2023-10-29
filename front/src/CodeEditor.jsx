import React from "react";
import CodeMirror from "@uiw/react-codemirror";

function CodeEditor(props) {

  const onChange = React.useCallback((value, viewUpdate) => {
    //console.log('value:', value);
    props.input(value)
  }, []);

  return (
    <CodeMirror
      className="scrollbar-track-gray-300 scrollbar-thumb-gray-500 scrollbar-thin rounded-md"
      height="590px"
      value='print("Hola mundo");'
      theme="dark"
      onChange={onChange}
    />
  );
}

export default CodeEditor;
