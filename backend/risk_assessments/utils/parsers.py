from defusedxml import ElementTree
from rest_framework.parsers import BaseParser
from rest_framework.exceptions import ParseError


class XMLRiskAssessmentParser(BaseParser):
    """
    Парсер для XML-запросов к эндпоинту drug-compatibility.
    Ожидает структуру:
        <Request Type="RiskAssessment">
            <RiskAssessmentData>
                <Drugs>
                    <string>амиодарон</string>
                    <string>парацетамол</string>
                </Drugs>
                <PatientProfile>
                    <Age>65</Age>
                    <Gender>woman</Gender>
                    <ContList>
                        <string>анемия</string>
                    </ContList>
                </PatientProfile>
            </RiskAssessmentData>
        </Request>
    """
    media_type = 'application/xml'

    def parse(self, stream, media_type=None, parser_context=None):
        try:
            # Читаем тело запроса
            data = stream.read().decode('utf-8')
            root = ElementTree.fromstring(data)
        except ElementTree.ParseError as exc:
            raise ParseError(f'Некорректный XML: {exc}')

        # Ищем блок RiskAssessmentData (может быть обёрнут в Request)
        risk_data = root.find('RiskAssessmentData')
        if risk_data is None:
            # Если нет, считаем корневой элемент самим блоком
            risk_data = root

        # Парсим препараты
        drugs_node = risk_data.find('Drugs')
        drugs = []
        if drugs_node is not None:
            for elem in drugs_node.findall('string'):
                if elem.text:
                    drugs.append(elem.text.strip())

        # Парсим профиль пациента (опционально)
        patient_profile = {}
        profile_node = risk_data.find('PatientProfile')
        if profile_node is not None:
            age_elem = profile_node.find('Age')
            if age_elem is not None and age_elem.text:
                try:
                    patient_profile['age'] = int(age_elem.text.strip())
                except ValueError:
                    raise ParseError('Поле Age должно быть целым числом')

            gender_elem = profile_node.find('Gender')
            if gender_elem is not None and gender_elem.text:
                patient_profile['gender'] = gender_elem.text.strip().lower()

            # Список противопоказаний (ContList)
            cont_list_node = profile_node.find('ContList')
            if cont_list_node is not None:
                cont_list = [el.text.strip() for el in cont_list_node.findall('string') if el.text]
                if cont_list:
                    patient_profile['contList'] = cont_list

        # Собираем итоговый словарь, который ожидает сериализатор
        result = {}
        result['drugs'] = drugs
        if patient_profile:
            result['patientProfile'] = patient_profile

        # Минимальная проверка
        if not result.get('drugs'):
            raise ParseError('В запросе отсутствует список Drugs')

        return result

