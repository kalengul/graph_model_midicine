const Router = require('express')
const router = new Router()
const documentsController = require('../controllers/documentsController')


router.post('/addnew', documentsController.AddNew)
router.get('/getall', documentsController.GetAll)
router.get('/:id', documentsController.GetById)
router.delete('/:id', documentsController.DeleteById)


module.exports = router