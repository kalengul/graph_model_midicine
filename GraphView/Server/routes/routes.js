const {Router} = require('express')
const router = Router()

const documentsRouter = require("./documentsRouter.js")
const graphRouter = require("./graphsRouter.js")

router.use('/documents', documentsRouter)
router.use('/graphs', graphRouter)

module.exports = router