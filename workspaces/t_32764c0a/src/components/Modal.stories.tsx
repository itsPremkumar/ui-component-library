import type { Meta, StoryObj } from '@storybook/react';
import { Modal } from './Modal';
import { useState } from 'react';

const meta: Meta<typeof Modal> = {
  title: 'Components/Modal',
  component: Modal,
  tags: ['autodocs'],
  argTypes: {
    size: { control: 'select', options: ['sm', 'md', 'lg', 'xl', 'full'] },
    closeOnOverlayClick: { control: 'boolean' },
    closeOnEscape: { control: 'boolean' },
    showCloseButton: { control: 'boolean' },
  },
};

export default meta;
type Story = StoryObj<typeof Modal>;

const ModalWrapper = (args: any) => {
  const [isOpen, setIsOpen] = useState(false);
  return (
    <>
      <button onClick={() => setIsOpen(true)}>Open Modal</button>
      <Modal {...args} isOpen={isOpen} onClose={() => setIsOpen(false)} />
    </>
  );
};

export const Default: Story = {
  render: (args) => (
    <ModalWrapper {...args} title="Modal Title">
      <p>This is the modal content.</p>
    </ModalWrapper>
  ),
};

export const Small: Story = {
  render: (args) => (
    <ModalWrapper {...args} size="sm" title="Small Modal">
      <p>Small modal content.</p>
    </ModalWrapper>
  ),
};

export const Large: Story = {
  render: (args) => (
    <ModalWrapper {...args} size="lg" title="Large Modal">
      <p>Large modal content with more space.</p>
    </ModalWrapper>
  ),
};

export const WithFooter: Story = {
  render: (args) => (
    <ModalWrapper
      {...args}
      title="Confirm Action"
      footer={
        <>
          <button onClick={() => {}}>Cancel</button>
          <button onClick={() => {}}>Confirm</button>
        </>
      }
    >
      <p>Are you sure you want to proceed?</p>
    </ModalWrapper>
  ),
};

export const NoCloseButton: Story = {
  render: (args) => (
    <ModalWrapper {...args} title="No Close" showCloseButton={false}>
      <p>This modal has no close button.</p>
    </ModalWrapper>
  ),
};
