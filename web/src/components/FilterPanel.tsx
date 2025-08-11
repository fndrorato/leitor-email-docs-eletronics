import React from 'react';
import { useTranslation } from 'react-i18next';
import AutoSelect from './form/AutoSelect';
import Label from './form/Label';
import DatePicker from './form/date-picker';
import Select from './form/Select';
import InputField from './form/input/InputField';
import Button from './ui/button/Button';
import { useFilters } from '../context/FilterContext';
import { format } from 'date-fns';
import { useState, useEffect } from 'react';
import axios from '../api/axios';

interface FilterPanelProps {
  isOpen: boolean;
  onClose: () => void;
}


const FilterPanel: React.FC<FilterPanelProps> = ({ isOpen, onClose }) => {
  const [isLoading, setIsLoading] = useState(false);
  const { t } = useTranslation();
  const {
    applyFilters,
  } = useFilters();
  
  const [localEmissor, setLocalEmissor] = useState('');
  const [localStartDate, setLocalStartDate] = useState('');
  const [localEndDate, setLocalEndDate] = useState('');
  const [localCdc, setLocalCdc] = useState('');
  const [localNumDoc, setLocalNumDoc] = useState('');
  const [localTipoDocumento, setLocalTipoDocumento] = useState('');
  
  const [documentTypes, setDocumentTypes] = useState<{value: string, label: string}[]>([]);
  
  useEffect(() => {
    const fetchDocumentTypes = async () => {
      try {
        const response = await axios.get('/api/v1/tipos-documento/');
        const types = response.data.results.map((doc: any) => ({
          value: doc.code.toString(),
          label: doc.name
        }));
        setDocumentTypes([{value: '', label: 'Todos'}, ...types]);
      } catch (err) {
        console.error('Error fetching document types:', err);
      }
    };
    
    fetchDocumentTypes();
  }, []);

  // if (!isOpen) return null;

const handleApplyFilters = async () => {
  setIsLoading(true);

  const MIN_DELAY = 500; // 500ms
  const delay = new Promise((resolve) => setTimeout(resolve, MIN_DELAY));

  await Promise.all([
    delay,
    applyFilters({
      emissor: localEmissor,
      startDate: localStartDate,
      endDate: localEndDate,
      cdc: localCdc,
      numDoc: localNumDoc,
      tipoDocumento: localTipoDocumento
    }),
  ]);

  setIsLoading(false);
};

  const visibilityClass = isOpen ? 'block' : 'hidden';

  return (
    <div className={`w-full px-6 py-4 bg-white border border-gray-200 rounded-lg shadow-lg dark:bg-gray-800 dark:border-gray-700 flex flex-row flex-nowrap items-end gap-4 overflow-visible z-50 relative ${visibilityClass}`}>
      <button
        onClick={onClose}
        className="absolute top-2 right-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
        aria-label="Close"
      >
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
          <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
      <AutoSelect
        label="Emissor"
        value={localEmissor}
        onChange={setLocalEmissor}
        loadOptions={async (inputValue) => {
          try {
            const response = await axios.get(`/api/v1/emissores/?search=${inputValue}`);
            return response.data.results.map((emissor: any) => ({
              value: emissor.id.toString(),
              label: emissor.nome,
            }));
          } catch (err) {
            console.error('Erro ao buscar emissores', err);
            return [];
          }
        }}
      />




      <div className="flex flex-col gap-1 w-[180px]">
        <Label htmlFor="startDatePicker">Data de Início</Label>
        <DatePicker id="startDatePicker" defaultDate={localStartDate ? new Date(localStartDate) : undefined} onChange={([date]) => setLocalStartDate(date ? format(date, 'yyyy-MM-dd') : '')} />
      </div>

      <div className="flex flex-col gap-1 w-[180px]">
        <Label htmlFor="endDatePicker">Data de Fim</Label>
        <DatePicker id="endDatePicker" defaultDate={localEndDate ? new Date(localEndDate) : undefined} onChange={([date]) => setLocalEndDate(date ? format(date, 'yyyy-MM-dd') : '')} />
      </div>

      <div className="flex flex-col gap-1 w-[180px]">
        <Label htmlFor="cdc">CDC</Label>
        <InputField id="cdc" type="text" value={localCdc} onChange={(e) => setLocalCdc(e.target.value)} />
      </div>

      <div className="flex flex-col gap-1 w-[180px]">
        <Label htmlFor="numDoc">Número do Documento</Label>
        <InputField id="numDoc" type="text" value={localNumDoc} onChange={(e) => setLocalNumDoc(e.target.value)} />
      </div>

      <div className="flex flex-col gap-1 w-[180px]">
        <Label htmlFor="tipoDocumento">Tipo de Documento</Label>
        <Select value={localTipoDocumento} onChange={(value) => setLocalTipoDocumento(value)} options={documentTypes} />
      </div>

      <div className="flex items-end">
        <Button onClick={handleApplyFilters} disabled={isLoading}>
          {isLoading ? t('Buscando...') : t('Buscar')}
        </Button>
      </div>
    </div>
  );

};

export default FilterPanel;