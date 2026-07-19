import React from 'react';
import { Modal } from './modal';
import { Button } from './button';

export const ConfirmDialog: React.FC<{ open: boolean; title?: string; description?: string; onConfirm: () => void; onCancel: () => void }> = ({ open, title, description, onConfirm, onCancel }) => {
  return (
    <Modal open={open} onClose={onCancel} title={title}>
      {description ? <p className="text-sm text-gray-600 dark:text-gray-300">{description}</p> : null}
      <div className="mt-4 flex justify-end space-x-2">
        <Button variant="secondary" onClick={onCancel}>Cancel</Button>
        <Button variant="destructive" onClick={onConfirm}>Confirm</Button>
      </div>
    </Modal>
  );
};

ConfirmDialog.displayName = 'ConfirmDialog';
