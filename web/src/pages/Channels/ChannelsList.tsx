import axios from '../../api/axios';
import PageBreadcrumb from "../../components/common/PageBreadCrumb";
import { PencilIcon, TrashBinIcon, PaperPlaneIcon } from '../../icons';
import { useState, useEffect } from "react";
import { useTranslation } from 'react-i18next';
import ChannelFormModal from './ChannelFormModal';
import ConfirmModal from '../../components/common/ConfirmModal';
import { useNavigate } from 'react-router-dom';
import {
  Table,
  TableBody,
  TableCell,
  TableHeader,
  TableRow,
} from '../../components/ui/table';

export interface Channel {
  id: number;
  name: string;
  description: string;
  invite: string;
  picture: string;
  verified: boolean;
  role: string;
  subscribers_count: number;
  status: string;

}

const ChannelsList: React.FC = () => {
  const { t } = useTranslation();
  const [channels, setChannels] = useState<Channel[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingChannel, setEditingChannel] = useState<Channel | null>(null);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [channelToDelete, setChannelToDelete] = useState<Channel | null>(null);
  const navigate = useNavigate();
 
   const fetchChannels = async () => {
     setLoading(true);
     setError(null);
     try {
       const response = await axios.get('/api/v1/channels/default/'); // Assuming a channels API endpoint
       setChannels(response.data);
     } catch (err) {
       setError('Failed to fetch channels.');
       console.error('Error fetching channels:', err);
     } finally {
       setLoading(false);
     }
   };
 
   useEffect(() => {
     fetchChannels();
   }, []);
 
   const handleOpenModal = (channel: Channel | null = null) => {
     setEditingChannel(channel);
     setIsModalOpen(true);
   };
 
   const handleCloseModal = () => {
     setEditingChannel(null);
     setIsModalOpen(false);
   };

   const handleOpenSendMessageModal = (channelId: number) => {
    navigate(`/channels/default/${channelId}`);
  };

 
   const handleChannelCreated = () => {
    fetchChannels(); // Refresh the channel list
  };

  const handleDeleteClick = (channel: Channel) => {
    setChannelToDelete(channel);
    setIsDeleteModalOpen(true);
  };

  const handleDeleteChannel = async () => {
    if (channelToDelete) {
      setIsDeleting(true);
      setDeleteError(null);
      try {
        // Assuming 'session_name' is available, perhaps from context or props
        // For now, I'll use a placeholder. You might need to adjust how session_name is obtained.
        const sessionName = 'default'; // Placeholder: Replace with actual session name logic
        await axios.delete(`/api/v1/channels/${sessionName}/${channelToDelete.id}/delete/`);
        fetchChannels(); // Refresh the channel list after deletion
        setIsDeleteModalOpen(false);
        setChannelToDelete(null);
      } catch (error) {
        console.error('Error deleting channel:', error);
        setDeleteError(t('failedToDeleteChannel'));
      } finally {
        setIsDeleting(false);
      }
    }
  };

  if (loading) {
    return <div>{t('loadingChannels')}</div>;
  }

  if (error) {
    return <div>{t('error')}: {error}</div>;
  }

  return (
    <>
      <PageBreadcrumb pageTitle={t('channelsList')} />
      <div className="p-2">
        <button
          onClick={() => handleOpenModal(null)}
          className="inline-flex items-center justify-center gap-2 rounded-lg transition  px-4 py-3 text-sm bg-brand-500 text-white shadow-theme-xs hover:bg-brand-600 disabled:bg-brand-300 mb-4"
        >
          {t('newChannel')}
        </button>
        <div className="overflow-hidden rounded-xl border border-gray-200 bg-white dark:border-white/[0.05] dark:bg-white/[0.03]">
          <div className="max-w-full overflow-x-auto">
            <Table>
              <TableHeader className="border-b border-gray-100 dark:border-white/[0.05]">
                <TableRow>
                  <TableCell isHeader className="px-5 py-3 font-medium text-gray-500 text-start text-theme-xs dark:text-gray-400">{t('picture')}</TableCell>
                  <TableCell isHeader className="px-5 py-3 font-medium text-gray-500 text-start text-theme-xs dark:text-gray-400">{t('name')}</TableCell>
                  <TableCell isHeader className="px-5 py-3 font-medium text-gray-500 text-start text-theme-xs dark:text-gray-400">{t('description')}</TableCell>
                  <TableCell isHeader className="px-5 py-3 font-medium text-gray-500 text-start text-theme-xs dark:text-gray-400">{t('invite')}</TableCell>
                  <TableCell isHeader className="px-5 py-3 font-medium text-gray-500 text-start text-theme-xs dark:text-gray-400">{t('subscribers')}</TableCell>

                  <TableCell isHeader className="px-5 py-3 font-medium text-gray-500 text-start text-theme-xs dark:text-gray-400">{t('actions')}</TableCell>
                </TableRow>
              </TableHeader>
              <TableBody className="divide-y divide-gray-100 dark:divide-white/[0.05]">
                {channels.map((channel) => (
                  <TableRow key={channel.id} className={channel.status === 'DELETED' ? 'bg-red-100' : ''}>
                    <TableCell className="px-4 py-3 text-gray-500 text-start text-theme-sm dark:text-gray-400">
                      {channel.picture && (
                        <img src={channel.picture} alt={channel.name} className="w-10 h-10 rounded-full object-cover" />
                      )}
                    </TableCell>
                    <TableCell className="px-4 py-3 text-gray-500 text-start text-theme-sm dark:text-gray-400">{channel.name}</TableCell>
                    <TableCell className="px-4 py-3 text-gray-500 text-start text-theme-sm dark:text-gray-400">{channel.description}</TableCell>
                    <TableCell className="px-4 py-3 text-gray-500 text-start text-theme-sm dark:text-gray-400">{channel.invite}</TableCell>
                    <TableCell className="px-4 py-3 text-gray-500 text-start text-theme-sm dark:text-gray-400">{channel.subscribers_count}</TableCell>

                    <TableCell className="px-4 py-3 text-gray-500 text-start text-theme-sm dark:text-gray-400">
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => handleOpenSendMessageModal(channel.id)}
                          className="text-green-500 hover:text-green-700"
                        >
                          <PaperPlaneIcon className="w-5 h-5" />
                        </button>
                        {/*
                        <button className="text-gray-500 hover:text-gray-700">
                          <ListIcon className="w-5 h-5" />
                        </button>
                        */}
                        <button
                          onClick={() => handleOpenModal(channel)}
                          className="text-blue-500 hover:text-blue-700"
                        >
                          <PencilIcon className="w-5 h-5" />
                        </button>
                        <button
                          className="text-red-500 hover:text-red-700"
                          onClick={() => handleDeleteClick(channel)}
                        >
                          <TrashBinIcon className="w-5 h-5" />
                        </button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </div>
      </div>

      <ChannelFormModal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        onChannelCreated={handleChannelCreated}
        editingChannel={editingChannel}
      />

      <ConfirmModal
        isOpen={isDeleteModalOpen}
        onClose={() => setIsDeleteModalOpen(false)}
        onConfirm={handleDeleteChannel}
        title={t('confirmExclusion')}
        message={t('confirmDeleteChannel', { channelName: channelToDelete?.name })}
        confirmText={isDeleting ? t('deleting') : t('yes')}
        confirmButtonDisabled={isDeleting}
      />
      {deleteError && <div className="text-red-500 text-sm mt-2">{deleteError}</div>}


    </>
  );
};

export default ChannelsList;