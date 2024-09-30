// documentSlices.js

import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

// Thunks for multipart upload

// Initiate Multipart Upload
export const initiateMultipartUpload = createAsyncThunk(
  'documents/initiateMultipartUpload',
  async (filename, { rejectWithValue }) => {
    try {
      const token = localStorage.getItem('IdToken');
      const url = `${process.env.REACT_APP_API_BASE_URL}/multipart_start_upload`;

      const response = await axios.post(
        url,
        { filename },
        {
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
        }
      );
      // Dump response headers
      console.log("Dumping response.data: ", response.data.uploadId);

      return response.data.uploadId;
    } catch (error) {
      return rejectWithValue(
        error.response?.data?.message || 'Failed to initiate upload.'
      );
    }
  }
);

// Generate Presigned URLs
export const generatePresignedUrls = createAsyncThunk(
  'documents/generatePresignedUrls',
  async ({ uploadId, filename, parts }, { rejectWithValue }) => {
    try {
      const token = localStorage.getItem('IdToken');
      const url = `${process.env.REACT_APP_API_BASE_URL}/multipart_generate_presigned_urls`;

      const response = await axios.post(
        url,
        { uploadId, filename, parts },
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );

      // Dump response headers
      console.log("Dumping response.headers: ", response.headers);

      return response.data.partUrls;
    } catch (error) {
      return rejectWithValue(
        error.response?.data?.message || 'Failed to generate presigned URLs.'
      );
    }
  }
);

export const uploadPart = createAsyncThunk(
  'documents/uploadPart',
  async ({ partUrl, partData, partNumber, totalParts }, thunkAPI) => {
    const { dispatch, rejectWithValue } = thunkAPI;
    console.log(`Uploading part ${partNumber}/${totalParts} to URL:`, partUrl);
    try {
      const response = await axios.put(partUrl, partData, {
        headers: {
          'Content-Type': 'application/octet-stream',
        },
        onUploadProgress: (progressEvent) => {
          const partProgress = Math.round(
            (progressEvent.loaded / partData.size) * 100
          );
          console.log(`Part ${partNumber} upload progress: ${partProgress}%`);
          dispatch(updateUploadProgress({ partNumber, partProgress }));
        },
      });

      // Dump response headers
      console.log("Dumping response.headers: ", response.headers);

      const etag = response.headers.etag || response.headers.ETag;
      if (!etag) {
        throw new Error('ETag not found in response headers');
      }
      console.log(`Upload complete for part ${partNumber}, ETag: ${etag}`);

      return { PartNumber: partNumber, ETag: etag };
    } catch (error) {
      const errorMessage =
        error.response?.data?.message || error.message || `Failed to upload part ${partNumber}.`;
      console.error(`Error uploading part ${partNumber}: ${errorMessage}`);
      return rejectWithValue(errorMessage);
    }
  }
);

// Upload a Single Part
/* export const uploadPart = createAsyncThunk(
  'documents/uploadPart',
  async (
    { partUrl, partData, partNumber, totalParts },
    { dispatch, rejectWithValue }
  ) => {
    console.log(`Uploading part ${partNumber}/${totalParts} to URL:`, partUrl);
    try {
      const response = await axios.put(partUrl, partData, {
        headers: {
          'Content-Type': 'application/octet-stream',
        },
        onUploadProgress: (progressEvent) => {
          const partProgress = Math.round(
            (progressEvent.loaded / progressEvent.total) * 100
          );
          console.log(`Part ${partNumber} upload progress: ${partProgress}%`);
          dispatch(updateUploadProgress({ partNumber, partProgress }));
        },
      });

      const etag = response.headers.etag || response.headers.ETag;
      console.log(`Upload complete for part ${partNumber}, ETag: ${etag}`);

      return { PartNumber: partNumber, ETag: etag };
    } catch (error) {
      const errorMessage =
        error.response?.data?.message || `Failed to upload part ${partNumber}.`;
      console.error(`Error uploading part ${partNumber}: ${errorMessage}`);
      return rejectWithValue(errorMessage);
    }
  }
);
*/

// Complete Multipart Upload
export const completeMultipartUpload = createAsyncThunk(
  'documents/completeMultipartUpload',
  async ({ uploadId, filename, parts }, { rejectWithValue }) => {
    try {
      const token = localStorage.getItem('IdToken');
      const url = `${process.env.REACT_APP_API_BASE_URL}/multipart_complete_upload`;

      await axios.post(
        url,
        { uploadId, filename, parts },
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );

      return filename;
    } catch (error) {
      return rejectWithValue(
        error.response?.data?.message || 'Failed to complete upload.'
      );
    }
  }
);

// Existing Thunks for Other Operations

export const fetchDocuments = createAsyncThunk(
  'documents/fetchDocuments',
  async (_, { rejectWithValue }) => {
    try {
      const token = localStorage.getItem('IdToken');

      const response = await axios.post(
        `${process.env.REACT_APP_API_BASE_URL}/list_assets`,
        {},
        {
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
        }
      );

      return response.data;
    } catch (error) {
      return rejectWithValue(
        error.response?.data || 'Failed to fetch documents'
      );
    }
  }
);

export const uploadDocument = createAsyncThunk(
  'documents/uploadDocument',
  async (payload, { rejectWithValue }) => {
    try {
      const token = localStorage.getItem('IdToken');

      const response = await axios.post(
        `${process.env.REACT_APP_API_BASE_URL}/upload_asset`,
        payload,
        {
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
        }
      );

      return response.data;
    } catch (error) {
      return rejectWithValue(
        error.response?.data || 'Failed to upload document'
      );
    }
  }
);

export const updateDocument = createAsyncThunk(
  'documents/updateDocument',
  async (formData, { rejectWithValue }) => {
    try {
      const token = localStorage.getItem('IdToken');

      const response = await axios.post(
        `${process.env.REACT_APP_API_BASE_URL}/update_asset`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
            Authorization: `Bearer ${token}`,
          },
        }
      );

      return response.data;
    } catch (error) {
      return rejectWithValue(
        error.response?.data || 'Failed to update document'
      );
    }
  }
);

export const deleteDocument = createAsyncThunk(
  'documents/deleteDocument',
  async (documentName, { rejectWithValue }) => {
    try {
      const token = localStorage.getItem('IdToken');

      await axios.post(
        `${process.env.REACT_APP_API_BASE_URL}/delete_assets`,
        { document_name: documentName },
        {
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
        }
      );

      return documentName;
    } catch (error) {
      return rejectWithValue(
        error.response?.data || 'Failed to delete document'
      );
    }
  }
);

export const viewDocument = createAsyncThunk(
  'documents/viewDocument',
  async (documentName, { rejectWithValue }) => {
    try {
      const token = localStorage.getItem('IdToken');

      const response = await axios.post(
        `${process.env.REACT_APP_API_BASE_URL}/view_asset`,
        { document_name: documentName },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      return { documentName, url: response.data.url };
    } catch (error) {
      return rejectWithValue(
        error.response?.data || 'Failed to retrieve document'
      );
    }
  }
);

// Slice

export const documentSlice = createSlice({
  name: 'documents',
  initialState: {
    items: [],
    loading: false,
    error: null,
    viewUrl: null,
    uploadProgress: {}, // State to track upload progress
  },
  reducers: {
    addDocument: (state, action) => {
      state.items.push(action.payload);
    },
    clearViewUrl: (state) => {
      state.viewUrl = null;
    },
    updateUploadProgress: (state, action) => {
      const { partNumber, partProgress } = action.payload;
      state.uploadProgress[partNumber] = partProgress;
    },
    resetUploadProgress: (state) => {
      state.uploadProgress = {};
    },
  },
  extraReducers: (builder) => {
    builder
      // initiateMultipartUpload
      .addCase(initiateMultipartUpload.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(initiateMultipartUpload.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(initiateMultipartUpload.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // generatePresignedUrls
      .addCase(generatePresignedUrls.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(generatePresignedUrls.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(generatePresignedUrls.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // uploadPart
      .addCase(uploadPart.pending, (state) => {
        state.error = null;
      })
      .addCase(uploadPart.fulfilled, (state) => { })
      .addCase(uploadPart.rejected, (state, action) => {
        state.error = action.payload;
      })
      // completeMultipartUpload
      .addCase(completeMultipartUpload.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(completeMultipartUpload.fulfilled, (state, action) => {
        state.loading = false;
        state.items.push({ document_name: action.payload });
      })
      .addCase(completeMultipartUpload.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // fetchDocuments
      .addCase(fetchDocuments.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchDocuments.fulfilled, (state, action) => {
        state.loading = false;
        state.items = action.payload;
      })
      .addCase(fetchDocuments.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // uploadDocument
      .addCase(uploadDocument.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(uploadDocument.fulfilled, (state, action) => {
        state.loading = false;
        state.items.push(action.payload);
      })
      .addCase(uploadDocument.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // updateDocument
      .addCase(updateDocument.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateDocument.fulfilled, (state, action) => {
        state.loading = false;
        const index = state.items.findIndex(
          (doc) => doc.document_name === action.payload.document_name
        );
        if (index !== -1) {
          state.items[index] = action.payload;
        }
      })
      .addCase(updateDocument.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // deleteDocument
      .addCase(deleteDocument.fulfilled, (state, action) => {
        state.items = state.items.filter(
          (doc) => doc.document_name !== action.payload
        );
      })
      // viewDocument
      .addCase(viewDocument.fulfilled, (state, action) => {
        state.viewUrl = action.payload.url;
      })
      .addCase(viewDocument.rejected, (state, action) => {
        state.error = action.payload;
      });
  },
});

export const {
  addDocument,
  clearViewUrl,
  updateUploadProgress,
  resetUploadProgress,
} = documentSlice.actions;

export default documentSlice.reducer;