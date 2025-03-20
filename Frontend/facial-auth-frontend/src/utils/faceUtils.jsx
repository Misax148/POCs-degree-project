export const adjustImageBrightness = (
  imageDataUrl,
  brightness = 15,
  contrast = 15
) => {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => {
      try {
        const canvas = document.createElement("canvas");
        canvas.width = img.width;
        canvas.height = img.height;
        const ctx = canvas.getContext("2d");

        ctx.drawImage(img, 0, 0);

        // Obtains image data
        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        const data = imageData.data;

        const brightnessFactor = 1 + brightness / 100;
        const contrastFactor = 1 + contrast / 100;

        for (let i = 0; i < data.length; i += 4) {
          // RGB applied
          data[i] = data[i] * brightnessFactor;
          data[i + 1] = data[i + 1] * brightnessFactor;
          data[i + 2] = data[i + 2] * brightnessFactor;

          data[i] = (data[i] - 128) * contrastFactor + 128;
          data[i + 1] = (data[i + 1] - 128) * contrastFactor + 128;
          data[i + 2] = (data[i + 2] - 128) * contrastFactor + 128;
        }

        ctx.putImageData(imageData, 0, 0);

        const processedImageUrl = canvas.toDataURL("image/jpeg", 0.9);
        resolve(processedImageUrl);
      } catch (error) {
        console.error("Error processing image:", error);
        resolve(imageDataUrl);
      }
    };

    img.onerror = () => {
      console.error("Error loading image for processing");
      resolve(imageDataUrl);
    };

    img.src = imageDataUrl;
  });
};


export const dataURLtoBlob = async (dataUrl) => {
  return await fetch(dataUrl).then((res) => res.blob());
};

export default {
  adjustImageBrightness,
  dataURLtoBlob,
};
