import React, { createContext, useState } from 'react';

export const GraphContext = createContext();

export const GraphProvider = ({ children }) => {
  const [graphCode, setGraphCode] = useState('');

  return (
    <GraphContext.Provider value={{ graphCode, setGraphCode }}>
      {children}
    </GraphContext.Provider>
  );
};