const Router = require('express')
const router = new Router()
const instructionsController = require('../controllers/instructionsController')


router.post('/update', instructionsController.Update)
router.get('/getall', instructionsController.GetAll)
router.get('/:id', instructionsController.GetById)
router.delete('/:id', instructionsController.DeleteById)


module.exports = router