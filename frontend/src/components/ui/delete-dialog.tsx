import React from 'react';
import { ConfirmDialog } from './confirm-dialog';

export const DeleteDialog: React.FC<{ open: boolean; itemName?: string; onDelete: () => void; onCancel: () => void }> = ({ open, itemName = 'item', onDelete, onCancel }) => {
  return (
    <ConfirmDialog open={open} title={`Delete ${itemName}?`} description={`Are you sure you want to delete this ${itemName}? This action cannot be undone.`} onConfirm={onDelete} onCancel={onCancel} />
  );
};

DeleteDialog.displayName = 'DeleteDialog';
