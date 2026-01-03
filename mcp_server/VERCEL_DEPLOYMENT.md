# Vercel Deployment Guide for TodoMore MCP Server

## Environment Variables Configuration

To fix the "Invalid Host Header" error on Vercel, you need to configure the `ALLOWED_HOSTS` environment variable.

### Steps to Configure on Vercel:

1. **Go to your Vercel project dashboard**
   - Navigate to https://vercel.com/dashboard
   - Select your MCP server project

2. **Navigate to Settings → Environment Variables**

3. **Add the ALLOWED_HOSTS variable:**
   - **Key:** `ALLOWED_HOSTS`
   - **Value:** Your Vercel deployment domain(s), comma-separated
   - **Environment:** Production (and optionally Preview/Development)

### Example Values:

For a single domain:
```
ALLOWED_HOSTS=todomore-mcp-git-master-muhammadsaifullah50s-projects.vercel.app
```

For multiple domains (e.g., production + custom domain):
```
ALLOWED_HOSTS=todomore-mcp-git-master-muhammadsaifullah50s-projects.vercel.app,mcp.yourdomain.com
```

### Important Notes:

1. **Port wildcards are added automatically** - The code will append `:*` to each host if not already present
2. **After adding the variable**, you MUST redeploy for changes to take effect
3. **For development/testing**, you can leave the variable empty (it will allow localhost only)

### How It Works:

The MCP server uses `TransportSecuritySettings` with DNS rebinding protection:

```python
transport_security=TransportSecuritySettings(
    enable_dns_rebinding_protection=True,
    allowed_hosts=["your-domain.vercel.app:*"],
    allowed_origins=["*"],
)
```

This is the **legitimate solution** that:
- ✅ Maintains security (DNS rebinding protection enabled)
- ✅ Works with Vercel's proxy infrastructure
- ✅ Follows MCP SDK best practices
- ✅ Avoids monkey patching

### Testing After Deployment:

```bash
# Health check
curl https://your-mcp-server.vercel.app/health

# Root endpoint
curl https://your-mcp-server.vercel.app/

# MCP SSE endpoint (should return valid response, not 421 error)
curl https://your-mcp-server.vercel.app/mcp/sse
```

### Troubleshooting:

**Still getting 421 errors?**
1. Verify the environment variable is set correctly in Vercel dashboard
2. Check that you've redeployed after setting the variable
3. Ensure the domain in ALLOWED_HOSTS matches exactly what Vercel uses
4. Check the deployment logs for the "✅ Allowed hosts configured" message

**Need to allow multiple domains?**
Separate them with commas, no spaces:
```
domain1.vercel.app,domain2.vercel.app,custom.domain.com
```

## Security Considerations

This solution maintains DNS rebinding protection while allowing specific trusted hosts. Unlike disabling the middleware entirely (via monkey patching), this approach:

- Validates the Host header against an allowlist
- Prevents DNS rebinding attacks
- Works seamlessly with Vercel's proxy infrastructure
- Follows official MCP SDK recommendations

## References

- [MCP SDK DNS Rebinding Protection Guide](https://github.com/modelcontextprotocol/python-sdk/issues/1798)
- [FastMCP TransportSecuritySettings Documentation](https://gofastmcp.com/deployment/server-configuration)
- [Vercel Environment Variables](https://vercel.com/docs/environment-variables/managing-environment-variables)
