type ClientEnvKey = `VITE_${string}`;

export function requireEnv(key: ClientEnvKey): string {
  const value = import.meta.env[key];
  if (value == null || String(value).trim() === '') {
    throw new Error(
        `Missing environment variable: ${key}. ` +
        `Define it in the frontend .env like this: \`${key}=http://localhost:8081\`.`
    );
  }
  return String(value);
}