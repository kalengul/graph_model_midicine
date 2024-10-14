export const Validator = (values, file) =>{
    const errors = {};

    if (!file && !values.schem_text) {
        errors.schem_text = "Пожалуйста, введите схему в формате JSON или загрузите файл";
    }

    if (!file && !values.schem_name) {
        errors.schem_name = "Пожалуйста, введите название схемы или загрузите файл";
    }

    return errors;
}