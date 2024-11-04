const {Router} = require('express')
const router = Router()

const documentsRouter = require("./documentsRouter.js")
const graphRouter = require("./graphsRouter.js")
const graphsValidRouter = require("./graphsValidRouter.js")

router.use('/documents', documentsRouter)
router.use('/graphs', graphRouter)
router.use('/graphsvalid', graphsValidRouter)

module.exports = router