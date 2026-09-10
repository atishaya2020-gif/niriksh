import React, { useState } from 'react';
import Modal from '../ui/Modal';
import Input from '../ui/Input';
import Select from '../ui/Select';
import Button from '../ui/Button';
import Toast from '../ui/Toast';

export const CrossStateModal = ({ isOpen, onClose }) => {
  const [targetState, setTargetState] = useState('Haryana');
  const [reason, setReason] = useState('');
  const [duration, setDuration] = useState('7');
  const [scope, setScope] = useState('READ_ONLY');
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    setSubmitted(true);
    setTimeout(() => {
      setSubmitted(false);
      onClose();
    }, 2000);
  };

  return (
    <>
      <Modal
        isOpen={isOpen}
        onClose={onClose}
        title="REQUEST CROSS-STATE INTELLIGENCE ACCESS"
        subtitle="Current Active State: Punjab • Requesting Multi-Jurisdictional Scope"
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="p-3 bg-purple-950/40 border border-purple-500/30 rounded-xl text-xs text-purple-200">
            <span className="font-bold text-cyan-400 font-mono-id block mb-1">
              PROTOTYPE ACCESS CONTROL SIMULATION
            </span>
            Cross-state data requests require multi-jurisdictional authorization and are logged in the immutable system audit trail.
          </div>

          <Select
            label="Requested Target State"
            value={targetState}
            onChange={(e) => setTargetState(e.target.value)}
            options={[
              { value: 'Haryana', label: 'Haryana' },
              { value: 'Delhi', label: 'Delhi NCR' },
              { value: 'Rajasthan', label: 'Rajasthan' },
              { value: 'Himachal Pradesh', label: 'Himachal Pradesh' }
            ]}
          />

          <Input
            label="Investigative Reason / Case Reference"
            placeholder="e.g. Shared logistics vehicle PB10XX1234 cross-border tracking"
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            required
          />

          <div className="grid grid-cols-2 gap-4">
            <Select
              label="Duration (Days)"
              value={duration}
              onChange={(e) => setDuration(e.target.value)}
              options={[
                { value: '3', label: '3 Days' },
                { value: '7', label: '7 Days' },
                { value: '14', label: '14 Days' },
                { value: '30', label: '30 Days' }
              ]}
            />

            <Select
              label="Access Scope"
              value={scope}
              onChange={(e) => setScope(e.target.value)}
              options={[
                { value: 'READ_ONLY', label: 'Read-Only Case Network' },
                { value: 'FULL_ANALYTICAL', label: 'Full Analytical & Ingestion Scope' }
              ]}
            />
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t border-purple-900/40">
            <Button variant="secondary" type="button" onClick={onClose}>
              Cancel
            </Button>
            <Button variant="cyan" type="submit">
              Submit Access Request
            </Button>
          </div>
        </form>
      </Modal>

      {submitted && (
        <Toast
          type="success"
          message="Cross-state access request submitted to State Liaison Officer."
        />
      )}
    </>
  );
};

export default CrossStateModal;
