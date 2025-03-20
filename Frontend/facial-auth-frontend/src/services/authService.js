import axios from 'axios';
import { dataURLtoBlob } from '../utils/faceUtils';

const API_URL = 'http://localhost:8000';

export const authService = {
  async register(username, imageDataUrl) {
    try {
      const imageBlob = await dataURLtoBlob(imageDataUrl);
      
      const formData = new FormData();
      formData.append('username', username);
      formData.append('image', imageBlob, 'face.jpg');
      
      const response = await axios.post(
        `${API_URL}/api/register`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          }
        }
      );
      
      return response.data;
    } catch (error) {
      if (error.response) {
        if (error.response.status === 409) {
          throw new Error('El usuario ya existe');
        } else if (error.response.data && error.response.data.detail) {
          throw new Error(error.response.data.detail);
        } else {
          throw new Error(`Error en el registro (${error.response.status})`);
        }
      } else if (error.request) {
        throw new Error('No se recibió respuesta del servidor');
      } else {
        throw new Error('Error al preparar la solicitud');
      }
    }
  },
  

  async verify(imageDataUrl) {
    try {
      const imageBlob = await dataURLtoBlob(imageDataUrl);
      
      const formData = new FormData();
      formData.append('image', imageBlob, 'face.jpg');
      
      const response = await axios.post(
        `${API_URL}/api/verify`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          }
        }
      );
      
      return response.data;
    } catch (error) {
      if (error.response) {
        if (error.response.data && error.response.data.detail) {
          throw new Error(error.response.data.detail);
        } else {
          throw new Error(`Error en la verificación (${error.response.status})`);
        }
      } else if (error.request) {
        throw new Error('No se recibió respuesta del servidor');
      } else {
        throw new Error('Error al preparar la solicitud');
      }
    }
  }
};

export default authService;