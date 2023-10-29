import React from "react";
import CodeEditor from "./CodeEditor";
import Consola from "./Consola";
import Example from "./Navbar";
import { useState, useContext } from "react";
import axios from "axios";
import { GraphContext } from './GraphContext';

function App() {
  const [fileContent, setFileContent] = useState("");
  const [consolita, setConsola] = useState("");
  const { setGraphCode } = useContext(GraphContext);
  let tablasimbolos = []

  function handleFileUpload(content) {
    setFileContent(content);
  }

  function handleCreateNewFile() {
    setFileContent("");
  }

  function handleSaveFile() {
    const content = fileContent; // Obtener el contenido de fileContent
    const blob = new Blob([content], { type: "tw" });
    const a = document.createElement("a");
    a.download = "archivo.tw";
    a.href = window.URL.createObjectURL(blob);
    a.onclick = () => {
      setTimeout(() => {
        window.URL.revokeObjectURL(a.href);
      }, 0);
    };
    a.click();
  }

  function handleSaveButtonClick() {
    handleSaveFile(fileContent);
  }

  const interpretar = async () => {
    console.log("Ejecutando...");
    try {
      setConsola("Ejecutando...");

      if (fileContent === "") {
        setConsola("Error: No hay codigo para ejecutar");
        console.log("Error: No hay codigo para ejecutar");
      } else {
        //console.log(fileContent);
        const response = await axios.post(
          "http://localhost:5000/execute",
          { entrada: fileContent }
        );
        console.log(response.data);
        //convertir a string la respuesta
        const respuestaString = response.data.map((mensaje) => mensaje).join("\n");

        setConsola(respuestaString);

      }
    } catch (error) {
      console.log(error);
      setConsola("Error en el servidor");
    }
  };

  



  return (
    <div className="h-screen bg-gray-800">
      <Example
        onCreateNewFile={handleCreateNewFile}
        onFileUpload={handleFileUpload}
        onSaveFile={handleSaveButtonClick}
        onPrintConsole={interpretar}
      />
      <div className="grid grid-cols-2 bg-gray-800 p-5 py-0 gap-5">
        <div className="inline-block py-3 px-2 text-sm text-gray-500 ">
          <h1>Codigo: </h1>
          <CodeEditor input = {setFileContent}/>
        </div>
        <div className="inline-block py-3 px-2 text-sm text-gray-500 ">
          <h1>Consola: </h1>
          <Consola consola={consolita}/>
        </div>
      </div>
    </div>
  );
}
export default App;
