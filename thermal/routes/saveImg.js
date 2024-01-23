const express = require('express');
const multer = require('multer');
const fs = require('fs').promises;
const path = require('path');

const router = express.Router();

// multer 설정
const storage = multer.diskStorage({
    destination: async (req, file, cb) => {
        const imgDir = path.join(__dirname, "..", 'imgs', 'thermal');
        try {
            await fs.mkdir(imgDir, { recursive: true });
            cb(null, imgDir);
        } catch (err) {
            cb(err, null);
        }
    },
    filename: (req, file, cb) => {
        cb(null, file.originalname);
    }
});

const upload = multer({ storage: storage });

// 이미지 업로드 라우트
router.post('/', upload.single('img'), (req, res) => {
    if (!req.file) {
        return res.status(400).send('No file uploaded.');
    }
    return res.status(200).send(`File uploaded successfully: ${req.file.filename}`);
});

module.exports = router;