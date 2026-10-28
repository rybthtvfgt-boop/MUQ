// Face Recognition System (Updated for Face Embeddings)
// استخدام face-api.js للتعرف الحقيقي على الوجه

class FaceRecognition {
    constructor() {
        // استخدام المحرك الجديد
        this.engine = faceEngine;
    }

    // البحث عن تطابق في قاعدة البيانات
    async findMatch(imageElement, faceDatabase) {
        return await this.engine.findMatch(imageElement, faceDatabase);
    }

    // التحقق من هوية محددة
    async verifyIdentity(imageElement, targetPerson) {
        return await this.engine.verifyIdentity(imageElement, targetPerson);
    }

    // التحقق من جودة الصورة
    async checkQuality(imageElement) {
        const detection = await this.engine.detectFace(imageElement);
        return this.engine.checkQuality(detection, imageElement);
    }

    // تحميل النماذج
    async loadModels() {
        return await this.engine.loadModels();
    }
}

const faceRecognition = new FaceRecognition();