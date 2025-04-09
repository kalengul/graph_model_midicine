import {Router} from 'express'
import {MarkForInstructions} from '../api/controllers/MarkForInstructions.mjs'
const router = Router()

const markForInstructions = new MarkForInstructions()


router.post('/addnewdrug', markForInstructions.AddNewDrug); //Добавление нового лс
router.post('/update', markForInstructions.UpdateDrugsStatus)//Обновление информации о статусах графоф лс
router.post('/update_by_id', markForInstructions.UpdateDrugByID)//Обновление информации о графах лс по шВ
router.get('/getstates', markForInstructions.GetGraphStatus); //Получение списка состояний
router.get('/getall', markForInstructions.GetAll); //Получение всех ЛС, графов и состояний
router.get('/export', markForInstructions.Export); //Получение всех ЛС, графов и состояний
router.delete('/deletedrug/:id', markForInstructions.DeleteDrug)//Удаление ЛС и всех схем

export default router;


