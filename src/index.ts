import {Hono} from 'hono'
import {cors} from 'hono/cors'

import Get from './routes/get'
import Patch from './routes/patch'
import Put from './routes/put'
import Delete from "./routes/delete"

import MpuCreate from './routes/mpu/create'
import MpuParts from './routes/mpu/parts'
import MpuAbort from './routes/mpu/abort'
import MpuComplete from './routes/mpu/complete'
import MpuSupport from './routes/mpu/support'
import MpuList from './routes/mpu/list'

import checkHeader from "./middleware/checkHeader"

const app = new Hono<{
  Bindings: {
    R2_BUCKET: R2Bucket
  }
}>()

app.use(cors())
app.get('/support_mpu', MpuSupport)
app.get('/', (c) => c.text('Hello R2! v2025.03.08.171740'))
app.use('*', checkHeader)

// multipart upload operations
app.get('/mpu/list', MpuList)
app.get('/mpu/parts', MpuParts)
app.post('/mpu/create/:key{.*}', MpuCreate)
app.put('/mpu/:key{.*}', MpuParts)
app.delete('/mpu/:key{.*}', MpuAbort)
app.post('/mpu/complete/:key{.*}', MpuComplete)

// normal r2 operations
app.get('/:key{.*}', Get)
app.patch('/', Patch)
app.put('/:key{.*}', Put)
app.delete('/:key{.*}', Delete)

app.all('*', c => {
  return c.text('404 Not Found')
})

export default app
