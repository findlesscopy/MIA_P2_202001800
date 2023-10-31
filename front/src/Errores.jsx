import Example from "./Navbar";
import axios from "axios";
import React, { useState, useEffect } from "react";
import './style.css'; // Importa un archivo CSS para los estilos

export default function Errores() {
  const [svgFiles, setSvgFiles] = useState([]);
  const [selectedImage, setSelectedImage] = useState(null);

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

  const openModal = (image) => {
    setSelectedImage(image);
  };

  const closeModal = () => {
    setSelectedImage(null);
  };

  return (
    <div className="h-screen bg-gray-800">
      <Example />
      <h1>Reportes</h1>
      <div className="image-list">
        {svgFiles.map((fileName, index) => (
          <div className="image-container" key={index} onClick={() => openModal(url + fileName)}>
            <img src={url + fileName} alt={fileName} />
            <div className="image-label">{fileName}</div>
          </div>
        ))}
      </div>

      {selectedImage && (
        <div className="modal" onClick={closeModal}>
          <div className="modal-content">
            <img src={selectedImage} alt="Zoomed Image" />
          </div>
        </div>
      )}
    </div>
  );
}
