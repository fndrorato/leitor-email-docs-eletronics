import { createContext, useContext, useState, ReactNode } from 'react';

interface FilterContextType {
  emissor: string;
  setEmissor: (emissor: string) => void;
  startDate: string;
  setStartDate: (startDate: string) => void;
  endDate: string;
  setEndDate: (endDate: string) => void;
  cdc: string;
  setCdc: (cdc: string) => void;
  numDoc: string;
  setNumDoc: (numDoc: string) => void;
  tipoDocumento: string;
  setTipoDocumento: (tipoDocumento: string) => void;
  applyFilters: (filters: { emissor: string, startDate: string, endDate: string, cdc: string, numDoc: string, tipoDocumento: string }) => void;
}

const FilterContext = createContext<FilterContextType | undefined>(undefined);

export const FilterProvider = ({ children }: { children: ReactNode }) => {
  const [emissor, setEmissor] = useState<string>('');
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');
  const [cdc, setCdc] = useState<string>('');
  const [numDoc, setNumDoc] = useState<string>('');
  const [tipoDocumento, setTipoDocumento] = useState<string>('');

  const applyFilters = (filters: { emissor: string, startDate: string, endDate: string, cdc: string, numDoc: string, tipoDocumento: string }) => {
    setEmissor(filters.emissor);
    setStartDate(filters.startDate);
    setEndDate(filters.endDate);
    setCdc(filters.cdc);
    setNumDoc(filters.numDoc);
    setTipoDocumento(filters.tipoDocumento);
    console.log('Applying filters:', filters);
  };

  return (
    <FilterContext.Provider
      value={{
        emissor,
        setEmissor,
        startDate,
        setStartDate,
        endDate,
        setEndDate,
        cdc,
        setCdc,
        numDoc,
        setNumDoc,
        tipoDocumento,
        setTipoDocumento,
        applyFilters,
      }}
    >
      {children}
    </FilterContext.Provider>
  );
};

export const useFilters = () => {
  const context = useContext(FilterContext);
  if (context === undefined) {
    throw new Error('useFilters must be used within a FilterProvider');
  }
  return context;
};