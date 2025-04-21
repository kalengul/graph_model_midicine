import { useState, useRef, KeyboardEvent } from 'react';
import { Badge, Form } from 'react-bootstrap';
import { FieldRenderProps } from 'react-final-form';

interface Recipient {
  id: string;
  email: string;
}

type RecipientsInputProps = FieldRenderProps<string[]> & {
  availableRecipients?: Recipient[];
};

export const RecipientsField = ({
  input,
  meta,
  availableRecipients = [],
}: RecipientsInputProps) => {
  const [inputValue, setInputValue] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  // Фильтрация доступных получателей
  const filteredRecipients = availableRecipients.filter(
    recipient =>
      recipient.email.toLowerCase().includes(inputValue.toLowerCase()) &&
      !input.value.some((r: Recipient) => r.id === recipient.id)
  );

  const handleAddRecipient = (recipient: Recipient) => {
    input.onChange([...input.value, recipient]);
    setInputValue('');
    setShowSuggestions(false);
    inputRef.current?.focus();
  };

  const handleRemoveRecipient = (id: string) => {
    input.onChange(input.value.filter((r: Recipient) => r.id !== id));
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && inputValue.trim()) {
      e.preventDefault();
      if (!filteredRecipients.length) {
        // Добавление нового email
        handleAddRecipient({
          id: Date.now().toString(),
          email: inputValue.trim(),
        });
      }
    } else if (e.key === 'Backspace' && !inputValue && input.value.length) {
      // Удаление последнего чипа
      handleRemoveRecipient(input.value[input.value.length - 1].id);
    }
  };

  return (
    <Form.Group className="mb-3">
      <Form.Label>Кому</Form.Label>
      <div 
        className={`border rounded p-2 d-flex flex-wrap align-items-center ${
          meta.error && meta.touched ? 'border-danger' : ''
        }`}
        style={{ minHeight: '44px' }}
        onClick={() => inputRef.current?.focus()}
      >
        {/* Чипы выбранных получателей */}
        {input.value.map((recipient: Recipient) => 
          <Badge 
            key={recipient.id} 
            bg="light" 
            text="dark"
            className="d-flex align-items-center me-1 mb-1"
          >
            {recipient.email}
            <button 
              type="button" 
              className="btn-close btn-close-white ms-1"
              style={{ fontSize: '0.5rem' }}
              onClick={(e) => {
                e.stopPropagation();
                handleRemoveRecipient(recipient.id);
              }}
              aria-label="Удалить"
            />
          </Badge>
        )}

        {/* Поле ввода */}
        <div className="position-relative flex-grow-1">
          <Form.Control
            type="text"
            ref={inputRef}
            value={inputValue}
            onChange={(e) => {
              setInputValue(e.target.value);
              setShowSuggestions(!!e.target.value);
            }}
            onKeyDown={handleKeyDown}
            onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
            className="border-0 shadow-none"
            style={{ minWidth: '150px' }}
            placeholder={input.value.length ? '' : 'Введите email...'}
          />

          {/* Выпадающие подсказки */}
          {showSuggestions && filteredRecipients.length > 0 && (
            <div 
              className="position-absolute w-100 bg-white mt-1 border rounded shadow-sm"
              style={{ zIndex: 10, maxHeight: '200px', overflowY: 'auto' }}
            >
              {filteredRecipients.map(recipient => (
                <div
                  key={recipient.id}
                  className="px-3 py-2 hover-bg-light cursor-pointer"
                  onClick={() => handleAddRecipient(recipient)}
                >
                  {recipient.email}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
      
      {meta.error && meta.touched && (
        <Form.Text className="text-danger">{meta.error}</Form.Text>
      )}
    </Form.Group>
  );
};