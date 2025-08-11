import React, { useState, useEffect } from 'react';
import { Modal } from '../../components/ui/modal';
import { useTranslation } from 'react-i18next';

interface AttachmentPreviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  file: File | null;
  onSend: (messageText: string, attachment: File) => void;
}

const AttachmentPreviewModal: React.FC<AttachmentPreviewModalProps> = ({
  isOpen,
  onClose,
  file,
  onSend,
}) => {
  const { t } = useTranslation();
  const [messageText, setMessageText] = useState('');
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  useEffect(() => {
    if (file) {
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
      return () => URL.revokeObjectURL(url);
    } else {
      setPreviewUrl(null);
    }
  }, [file]);

  if (!isOpen || !file) {
    return null;
  }

  const handleSend = () => {
    if (file) {
      onSend(messageText, file);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} className="w-11/12 md:w-1/2 lg:w-1/3 p-4 rounded-lg shadow-lg bg-white dark:bg-gray-900">
      <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">{t('attachment_preview_modal.title')}</h2>
      <div className="mb-4">
        {file.type.startsWith('image/') && (
          <img src={previewUrl || ''} alt="Preview" className="max-w-full h-auto rounded-md mx-auto" />
        )}
        {file.type.startsWith('video/') && (
          <video src={previewUrl || ''} controls className="max-w-full max-h-64 rounded-md mx-auto"></video>
        )}
        {!file.type.startsWith('image/') && !file.type.startsWith('video/') && (
          <p className="text-gray-700 dark:text-gray-300">{t('attachment_preview_modal.unsupported_type')}</p>
        )}
      </div>
      <input
        type="text"
        placeholder={t('attachment_preview_modal.add_a_message')}
        className="w-full p-2 border border-gray-300 rounded-md mb-4 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder:text-gray-400 dark:placeholder:text-gray-500"
        value={messageText}
        onChange={(e) => setMessageText(e.target.value)}
      />
      <div className="flex justify-end space-x-2">
        <button
          type="button"
          onClick={onClose}
          className="px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600"
        >
          {t('attachment_preview_modal.cancel')}
        </button>
        <button
          type="button"
          onClick={handleSend}
          className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
        >
          {t('attachment_preview_modal.send')}
        </button>
      </div>
    </Modal>
  );
};

export default AttachmentPreviewModal;