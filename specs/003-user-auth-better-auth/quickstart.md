# Quickstart: User Authentication (Better Auth)

Follow these steps to set up and run the application with User Authentication enabled.

## 1. Environment Variables

Update both `.env` files with the `BETTER_AUTH_SECRET`.

### Backend (`backend/.env`)
```bash
BETTER_AUTH_SECRET=your_high_entropy_secret_here
# Optional but recommended
JWT_ISSUER=todo-auth
JWT_AUDIENCE=todo-api
```

### Frontend (`frontend/.env.local`)
```bash
BETTER_AUTH_SECRET=your_high_entropy_secret_here
BETTER_AUTH_URL=http://localhost:3000
```

## 2. Dependencies

Install the required packages.

### Backend
```bash
cd backend
pip install python-jose[cryptography]
```

### Frontend
```bash
cd frontend
npm install better-auth
```

## 3. Database Initialization

Since Better Auth manages its own tables, you need to let it create the schema.

```bash
# In the frontend directory
npx better-auth migrate
```

## 4. Running the Application

1. Start the Docker services: `docker-compose up -d`
2. The landing page is available at `http://localhost:3000`.
3. Click **Sign Up** to create an account.
4. After signup, you will be redirected to the **Dashboard** at `http://localhost:3000/dashboard`.
5. Your API requests will now automatically include the JWT token.

## 5. Verification

To verify the integration:
1. Open the browser DevTools (Network tab).
2. Create a task.
3. Inspect the request to `http://localhost:8000/api/v1/tasks`.
4. Verify the `Authorization: Bearer <token>` header is present.
5. Hit the `GET /api/v1/users/me` endpoint to see your authenticated profile.
