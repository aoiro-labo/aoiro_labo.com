import { S3Client, PutObjectCommand } from "@aws-sdk/client-s3";
import fs from "node:fs";
import path from "node:path";
import "dotenv/config";

const {
  R2_ACCESS_KEY_ID,
  R2_SECRET_ACCESS_KEY,
  R2_ENDPOINT,
  R2_BUCKET_NAME,
  R2_PUBLIC_DOMAIN,
} = process.env;

const s3Client = new S3Client({
  endpoint: R2_ENDPOINT,
  region: "auto",
  credentials: {
    accessKeyId: R2_ACCESS_KEY_ID,
    secretAccessKey: R2_SECRET_ACCESS_KEY,
  },
});

async function main() {
  const filePath = process.argv[2];
  if (!filePath) {
    console.error("No file path provided.");
    process.exit(1);
  }

  const folderName = "blog"; 
  const fileName = path.basename(filePath);
  const objectKey = `${folderName}/${fileName}`;

  try {
    const fileContent = fs.readFileSync(filePath);
    await s3Client.send(new PutObjectCommand({
      Bucket: R2_BUCKET_NAME,
      Key: objectKey,
      Body: fileContent,
      ContentType: getMimeType(fileName),
    }));

    const baseUrl = R2_PUBLIC_DOMAIN.replace(/\/$/, "");
    console.log(`${baseUrl}/${objectKey}`);
  } catch (error) {
    console.error("Upload error:", error.message);
    process.exit(1);
  }
}

function getMimeType(fileName) {
  const ext = path.extname(fileName).toLowerCase();
  const map = { ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp", ".gif": "image/gif" };
  return map[ext] || "application/octet-stream";
}

main();