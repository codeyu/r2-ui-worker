import { Context } from "hono"

export default async function (c: Context) {
    try {
        const env = c.env
        // 获取 R2 bucket 的绑定
        const bucket = env.R2_BUCKET
        // 获取 bucket 名称
        const bucketName = bucket.name

        // 获取分页参数
        const cursor = c.req.query('cursor')
        const perPage = parseInt(c.req.query('per_page') || '1000')  // 默认1000，最大1000

        // 构建基础 URL
        let url = `https://api.cloudflare.com/client/v4/accounts/${env.CLOUDFLARE_ACCOUNT_ID}/r2/buckets/${bucketName}/uploads?per_page=${perPage}`
        
        // 如果有 cursor，添加到 URL
        if (cursor) {
            url += `&cursor=${encodeURIComponent(cursor)}`
        }

        // 发起请求
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${env.CLOUDFLARE_API_TOKEN}`,
                'Content-Type': 'application/json'
            }
        })

        if (!response.ok) {
            const error = await response.json()
            return c.json({
                success: false,
                error: error.errors?.[0]?.message || 'Failed to fetch uploads'
            }, response.status)
        }

        const data = await response.json()
        
        // 返回数据和分页信息
        return c.json({
            success: true,
            data: data.result,
            pagination: {
                cursor: data.result_info?.cursor,  // 下一页的 cursor
                has_more: data.result_info?.has_more || false
            }
        })

    } catch (error) {
        console.error('Error fetching uploads:', error)
        return c.json({
            success: false,
            error: 'Internal server error'
        }, 500)
    }
}