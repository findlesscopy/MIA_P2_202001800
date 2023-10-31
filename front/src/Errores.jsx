import Example from "./Navbar";
import axios from "axios";
import React, { useState, useEffect } from "react";

export default function Errores() {
  const [svgFiles, setSvgFiles] = useState([]);

  useEffect(() => {
    // Realizar la solicitud GET para obtener la lista de nombres de archivos SVG.
    axios.get("http://3.12.148.84/reportes")
      .then((response) => {
        setSvgFiles(response.data); // Almacena la lista en el estado.
      })
      .catch((error) => {
        console.error("Error al obtener la lista de archivos SVG", error);
      });
  }, []);

  const url = "https://front-proyecto2-mia-202001800.s3.us-east-2.amazonaws.com/reportes/";
  return (
    <div className="h-screen bg-gray-800">
      <Example />
      <h1>Reportes</h1>
      <div>
        {svgFiles.map((fileName, index) => (
          <img
            key={index}
            src={"https://front-proyecto2-mia-202001800.s3.us-east-2.amazonaws.com/reportes/d11.svg"}
            alt={fileName}
          />
        ))}
      </div>
    </div>
  );
}