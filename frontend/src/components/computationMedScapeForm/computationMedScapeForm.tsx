import { Form as FinalForm, Field } from 'react-final-form';
import { Form, Button } from 'react-bootstrap';
import { RecipientsField } from './RecipientsField';

import { IDrug } from '../../interfaces/Interfaces';
import { ComputationMedScapeValidator } from './computationMedScapeValidator';


const TestDrug: IDrug[] = [
  { id: '1', drug_name: 'Амиодарон' },
  { id: '2', drug_name: 'Лоротадин' },
  { id: '3', drug_name: 'Гликолиевая кислота' },
];

export const ComputationMedScapeForm = () => {
    const SendHandler =async (values: ISendDrugData)=>{
        //window.alert(values.drug_name)
    }

  return (
    <FinalForm<FormValues>
      onSubmit={onSubmit}
      validate={(values)=>ComputationMedScapeValidator(values)}
      initialValues={{ recipients: [] }}
      render={({ handleSubmit, submitting }) => (
        <form onSubmit={handleSubmit}>
          <Field<string[]>
            name="recipients"
            component={RecipientsField}
            availableRecipients={mockRecipients}
          />
          
          <Field name="subject">
            {({ input, meta }) => (
              <Form.Group className="mb-3">
                <Form.Label>Тема</Form.Label>
                <Form.Control
                  {...input}
                  type="text"
                  placeholder="Введите тему"
                  isInvalid={meta.touched && meta.error}
                />
                {meta.error && meta.touched && (
                  <Form.Control.Feedback type="invalid">
                    {meta.error}
                  </Form.Control.Feedback>
                )}
              </Form.Group>
            )}
          </Field>

          <Field name="message">
            {({ input, meta }) => (
              <Form.Group className="mb-3">
                <Form.Label>Сообщение</Form.Label>
                <Form.Control
                  {...input}
                  as="textarea"
                  rows={5}
                  isInvalid={meta.touched && meta.error}
                />
              </Form.Group>
            )}
          </Field>

          <Button 
            variant="primary" 
            type="submit" 
            disabled={submitting}
          >
            Отправить
          </Button>
        </form>
      )}
    />
  );
};