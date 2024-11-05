const Router = require('express')
const router = new Router()
const graphsValidController = require('../controllers/graphsValidController')

router.post('/addnew', graphsValidController.AddNew)
router.get('/download/:id', graphsValidController.DownloadById)
router.get('/all/download/:id', graphsValidController.DownloadAll)
router.get('/all/:id', graphsValidController.GetAll)
router.get("/:id", graphsValidController.GetById)
router.delete('/:id', graphsValidController.DeleteById)

module.exports = router