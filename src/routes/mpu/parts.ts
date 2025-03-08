import {Context} from "hono"

export default async function (c: Context) {
  try {
    const env = c.env
    const bucket = env.R2_BUCKET
    const bucketName = bucket.name

    // 从查询参数获取 key
    const key = c.req.query('key')

    if (!key) {
      return c.json({
        success: false,
        error: 'Missing required parameter: key'
      }, 400)
    }

    // 1. 首先获取所有未完成的上传列表
    const listUrl = `https://api.cloudflare.com/client/v4/accounts/${env.CLOUDFLARE_ACCOUNT_ID}/r2/buckets/${bucketName}/uploads`
    const listResponse = await fetch(listUrl, {
      headers: {
        'Authorization': `Bearer ${env.CLOUDFLARE_API_TOKEN}`,
        'Content-Type': 'application/json'
      }
    })

    if (!listResponse.ok) {
      const error = await listResponse.json()
      return c.json({
        success: false,
        error: error.errors?.[0]?.message || 'Failed to fetch uploads'
      }, listResponse.status as any)
    }

    const uploads = await listResponse.json()
    
    // 2. 查找匹配的文件
    const upload = uploads.result.find((u: any) => u.key === key)

    if (!upload) {
      return c.json({
        success: false,
        error: 'No active multipart upload found for this key'
      }, 404)
    }

    // 3. 获取分片列表
    const partsUrl = `https://api.cloudflare.com/client/v4/accounts/${env.CLOUDFLARE_ACCOUNT_ID}/r2/buckets/${bucketName}/uploads/${upload.uploadId}/parts?key=${encodeURIComponent(key)}`

    const partsResponse = await fetch(partsUrl, {
      headers: {
        'Authorization': `Bearer ${env.CLOUDFLARE_API_TOKEN}`,
        'Content-Type': 'application/json'
      }
    })

    if (!partsResponse.ok) {
      const error = await partsResponse.json()
      return c.json({
        success: false,
        error: error.errors?.[0]?.message || 'Failed to fetch parts'
      }, partsResponse.status as any)
    }

    const parts = await partsResponse.json()
    return c.json({
      success: true,
      data: {
        uploadId: upload.uploadId,
        parts: parts.result
      }
    })

  } catch (error) {
    console.error('Error fetching parts:', error)
    return c.json({
      success: false,
      error: 'Internal server error'
    }, 500)
  }
}
