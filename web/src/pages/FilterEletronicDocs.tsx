import {
  Table,
  TableBody,
  TableCell,
  TableHeader,
  TableRow,
} from "../components/ui/table";
import Button from "../components/ui/button/Button";
import { format } from 'date-fns';

import { useState, useEffect } from "react";
import axios from '../api/axios';
import { useTranslation } from 'react-i18next';
import { useFilters } from '../context/FilterContext';
import { useAuth } from "../context/AuthContext";
import { Modal } from "../components/ui/modal";
import { useNavigate } from "react-router-dom";

// Define the TypeScript interface for the table rows
interface Document {
  cdc: string;
  tipo_documento: {
    code: number;
    name: string;
  };
  est: string;
  pun_exp: string;
  num_doc: string;
  emissor: {
    code: string;
    nome: string;
    nome_fantasia: string;
    cidade: {
      code: string;
      name: string;
      departamento: {
        code: string;
        name: string;
      };
    };
  };
  fecha_emision: string;
  monto_total_formatado: string;
  created_at: string;
  updated_at: string;
}


export default function FilterEletronicDocs() {
  const { t } = useTranslation();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { emissor, startDate, endDate, cdc, numDoc, tipoDocumento, applyFilters: contextApplyFilters } = useFilters();
  const [nextPageUrl, setNextPageUrl] = useState<string | null>(null);
  const [previousPageUrl, setPreviousPageUrl] = useState<string | null>(null);
  const [totalCount, setTotalCount] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const { user } = useAuth();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [xmlContent, setXmlContent] = useState("");
  const navigate = useNavigate();
  // const location = useLocation();

  const fetchDocuments = async (url?: string) => {
    try {
      setLoading(true);
      const apiUrl = url || '/api/v1/documentos/';
      const params: any = { limit: 100 }; // Set limit to 100

      if (user?.company) {
        params.company = user.company;
      }

      if (!url) { // Only apply filters if not navigating via next/previous URLs
        console.log('Applying filters:', { startDate, endDate, emissor, cdc, numDoc, tipoDocumento });
        if (startDate) params.start_date = startDate;
        if (endDate) params.end_date = endDate;
        if (emissor) params.emissor = emissor;
        if (cdc) params.cdc = cdc;
        if (numDoc) params.num_doc__icontains = numDoc;
        if (tipoDocumento) params.tipo_documento = tipoDocumento;

        const searchParams = new URLSearchParams();
        if (startDate) searchParams.set('start_date', startDate);
        if (endDate) searchParams.set('end_date', endDate);
        if (emissor) searchParams.set('emissor', emissor);
        if (cdc) searchParams.set('cdc', cdc);
        if (numDoc) searchParams.set('num_doc__icontains', numDoc);
        if (tipoDocumento) searchParams.set('tipo_documento', tipoDocumento);
        navigate(`?${searchParams.toString()}`, { replace: true });

      } else {
        // Extract existing params from URL if navigating via next/previous
        const urlParams = new URLSearchParams(url.split('?')[1]);
        urlParams.forEach((value, key) => {
          params[key] = value;
        });
      }

      const response = await axios.get(apiUrl, { params });
      setDocuments(response.data.results);
      setNextPageUrl(response.data.next);
      setPreviousPageUrl(response.data.previous);
      setTotalCount(response.data.count);

      // Calculate current page based on offset
      const currentOffset = url ? parseInt(new URLSearchParams(url.split('?')[1]).get('offset') || '0') : 0;
      setCurrentPage(Math.floor(currentOffset / 100) + 1);

    } catch (err) {
      setError('Failed to fetch documents.');
      console.error('Error fetching documents:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user) {
      fetchDocuments();
    }
  }, [emissor, startDate, endDate, cdc, numDoc, tipoDocumento, contextApplyFilters, user]);

  const handleNextPage = () => {
    if (nextPageUrl) {
      fetchDocuments(nextPageUrl);
    }
  };

  const handlePrevPage = () => {
    if (previousPageUrl) {
      fetchDocuments(previousPageUrl);
    }
  };

  const totalPages = Math.ceil(totalCount / 100);

  if (loading) {
    return <div>{t('common.loading')}</div>;
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  const handleDownload = async (type: 'xml' | 'pdf', cdc: string) => {
    try {
      const url = `/api/v1/documentos/download-${type}/${cdc}/`;
      const response = await axios.get(url, {
        responseType: 'blob', // Important for downloading files
      });

      const filename = `${cdc}.${type}`;
      const blob = new Blob([response.data], { type: response.headers['content-type'] });
      const link = document.createElement('a');
      link.href = window.URL.createObjectURL(blob);
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(link.href);
    } catch (err) {
      console.error(`Error downloading ${type} for cdc ${cdc}:`, err);
      alert(`Failed to download ${type} file.`);
    }
  };

  const handleShowXml = async (cdc: string) => {
    try {
      const url = `/api/v1/documentos/download-xml/${cdc}/`;
      const response = await axios.get(url, {
        responseType: 'text',
      });
      setXmlContent(response.data);
      setIsModalOpen(true);
    } catch (err) {
      console.error(`Error fetching xml for cdc ${cdc}:`, err);
      alert(`Failed to fetch xml file.`);
    }
  };

  return (
    <div className="overflow-hidden rounded-2xl border border-gray-200 bg-white px-4 pb-3 pt-4 dark:border-gray-800 dark:bg-white/[0.03] sm:px-6">
      <div className="max-w-full overflow-x-auto">
        <Table>
          {/* Table Header */}
          <TableHeader className="border-gray-100 dark:border-gray-800 border-y">
            <TableRow>
              <TableCell
                isHeader
                className="py-3 font-medium text-gray-500 text-start text-theme-xs dark:text-gray-400"
              >
                Fecha Emisión
              </TableCell>
              <TableCell
                isHeader
                className="py-3 font-medium text-gray-500 text-start text-theme-xs dark:text-gray-400"
              >
                RUC
              </TableCell>
              <TableCell
                isHeader
                className="py-3 font-medium text-gray-500 text-start text-theme-xs dark:text-gray-400"
              >
                Empresa
              </TableCell>
              <TableCell
                isHeader
                className="py-3 font-medium text-gray-500 text-start text-theme-xs dark:text-gray-400"
              >
                Tipo Documento
              </TableCell>
              <TableCell
                isHeader
                className="py-3 font-medium text-gray-500 text-center text-theme-xs dark:text-gray-400"
              >
                Número Doc
              </TableCell>
              <TableCell
                isHeader
                className="py-3 font-medium text-gray-500 text-center text-theme-xs dark:text-gray-400"
              >
                Monto
              </TableCell>
              <TableCell
                isHeader
                className="py-3 font-medium text-gray-500 text-start text-theme-xs dark:text-gray-400"
              >
                Acciones
              </TableCell>
            </TableRow>
          </TableHeader>

          {/* Table Body */}

          <TableBody className="divide-y divide-gray-100 dark:divide-gray-800">
            {documents.map((doc, index) => (
              <TableRow key={doc.cdc} className={`${index % 2 === 0 ? 'bg-gray-50 dark:bg-gray-800' : ''}`}>
                <TableCell className="py-2 text-theme-sm text-gray-900 dark:text-white/90">
                  {format(new Date(doc.fecha_emision), 'dd/MM/yyyy')}
                </TableCell>
                <TableCell className="py-2 text-theme-sm text-gray-900 dark:text-white/90">
                  {doc.emissor.code}
                </TableCell>
                <TableCell className="py-2 text-theme-sm text-gray-900 dark:text-white/90">
                  {doc.emissor.nome}
                </TableCell>
                <TableCell className="py-2 text-theme-sm text-gray-900 dark:text-white/90">
                  {doc.tipo_documento.name}
                </TableCell>
                <TableCell className="py-2 text-center text-theme-sm text-gray-900 dark:text-white/90">
                  {`${doc.est}-${doc.pun_exp}-${doc.num_doc}`}
                </TableCell>
                <TableCell className="py-2 text-end text-theme-sm text-gray-900 dark:text-white/90">
                  {doc.monto_total_formatado}
                </TableCell>
                <TableCell className="py-2 text-center text-theme-sm text-gray-900 dark:text-white/90">
                  <div className="flex justify-center space-x-2">
                    <img
                      src="/images/icons/xml-document.svg"
                      alt="XML"
                      className="w-6 h-6 cursor-pointer"
                      onClick={() => handleShowXml(doc.cdc)}
                    />
                    <img
                      src="/images/icons/pdf-file.svg"
                      alt="PDF"
                      className="w-6 h-6 cursor-pointer"
                      onClick={() => handleDownload('pdf', doc.cdc)}
                    />
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
        {/* Pagination Controls */}
        <div className="flex items-center justify-between mt-4">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Page {currentPage} of {totalPages}
          </p>
          <div className="flex space-x-2">
            <Button 
              onClick={handlePrevPage} 
              disabled={!previousPageUrl}
              className={!previousPageUrl ? "opacity-50 cursor-not-allowed" : ""}
            >
              Previous
            </Button>
            <Button 
              onClick={handleNextPage} 
              disabled={!nextPageUrl}
              className={!nextPageUrl ? "opacity-50 cursor-not-allowed" : ""}
            >
              Next
            </Button>
          </div>
        </div>
      </div>

      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} isFullscreen={true} showCloseButton={false}>
        <div className="p-4">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-bold dark:text-white">XML Content</h2>
            <div>
              <Button onClick={() => handleDownload('xml', xmlContent)} className="mr-2">Download</Button>
              <Button onClick={() => setIsModalOpen(false)}>Close</Button>
            </div>
          </div>
          <pre className="bg-gray-100 dark:bg-gray-800 p-4 rounded-lg overflow-auto text-gray-800 dark:text-gray-200">
            <code>{xmlContent}</code>
          </pre>
        </div>
      </Modal>

    </div>
  );
}