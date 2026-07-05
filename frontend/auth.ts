import { betterAuth } from "better-auth";
import { jwt } from "better-auth/plugins";
import { Pool } from "pg";

const databaseUrl = (process.env.DATABASE_URL || "").replace(
    /^postgresql:\/\//,
    "postgres://"
);

export const auth = betterAuth({
    baseURL: process.env.BETTER_AUTH_URL || "http://localhost:3000",
    database: new Pool({
        connectionString: databaseUrl,
    }),
    emailAndPassword: {
        enabled: true,
    },
    // Configure table and column names to match PostgreSQL snake_case convention
    user: {
        fields: {
            emailVerified: "email_verified",
            createdAt: "created_at",
            updatedAt: "updated_at",
        },
    },
    session: {
        fields: {
            userId: "user_id",
            expiresAt: "expires_at",
            ipAddress: "ip_address",
            userAgent: "user_agent",
            createdAt: "created_at",
            updatedAt: "updated_at",
        },
    },
    account: {
        fields: {
            userId: "user_id",
            accountId: "account_id",
            providerId: "provider_id",
            accessToken: "access_token",
            refreshToken: "refresh_token",
            accessTokenExpiresAt: "access_token_expires_at",
            refreshTokenExpiresAt: "refresh_token_expires_at",
            createdAt: "created_at",
            updatedAt: "updated_at",
        },
    },
    verification: {
        fields: {
            expiresAt: "expires_at",
            createdAt: "created_at",
            updatedAt: "updated_at",
        },
    },
    // Note: jwks table uses camelCase columns (publicKey, privateKey, createdAt)
    // because Better Auth JWT plugin doesn't support field mapping for jwks
    plugins: [
        jwt({
            jwt: {
                issuer: "todo-auth",
                audience: "todo-api",
            }
        })
    ]
});
