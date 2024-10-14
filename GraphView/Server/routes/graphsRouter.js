const Router = require('express')
const router = new Router()
const graphsController = require('../controllers/graphsController')

router.post('/addnew', graphsController.AddNew)
router.get('/download/:id', graphsController.DownloadById)
router.get('/all', graphsController.GetAll)
router.get("/:id", graphsController.GetById)
router.delete('/:id', graphsController.DeleteById)

module.exports = router