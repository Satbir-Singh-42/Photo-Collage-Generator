import { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';

interface ImageUploaderProps {
  onFilesSelected: (files: File[]) => void;
  disabled?: boolean;
  isAddMore?: boolean;
}

const ACCEPTED_FORMATS = {
  'image/jpeg': ['.jpg', '.jpeg'],
  'image/png': ['.png'],
  'image/gif': ['.gif'],
  'image/bmp': ['.bmp'],
  'image/webp': ['.webp'],
  'image/tiff': ['.tiff', '.tif'],
};

export default function ImageUploader({ onFilesSelected, disabled, isAddMore }: ImageUploaderProps) {
  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles.length > 0) {
        onFilesSelected(acceptedFiles);
      }
    },
    [onFilesSelected]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: ACCEPTED_FORMATS,
    disabled,
    multiple: true,
  });

  return (
    <div
      {...getRootProps()}
      className={`upload-zone ${isDragActive ? 'active' : ''} ${disabled ? 'disabled' : ''} ${isAddMore ? 'add-more' : ''}`}
    >
      <input {...getInputProps()} />
      <div className="upload-content">
        <div className="upload-icon">
          {isAddMore ? (
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="12" y1="5" x2="12" y2="19" />
              <line x1="5" y1="12" x2="19" y2="12" />
            </svg>
          ) : (
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="17 8 12 3 7 8" />
              <line x1="12" y1="3" x2="12" y2="15" />
            </svg>
          )}
        </div>
        {isDragActive ? (
          <p>Drop images here...</p>
        ) : isAddMore ? (
          <>
            <p>Add More Images</p>
            <p className="upload-hint">Drop or click to add</p>
          </>
        ) : (
          <>
            <p>Drag & drop images here</p>
            <p className="upload-hint">or click to browse</p>
          </>
        )}
        {!isAddMore && (
          <p className="upload-formats">
            JPG, PNG, GIF, BMP, WebP, TIFF
          </p>
        )}
      </div>
    </div>
  );
}
