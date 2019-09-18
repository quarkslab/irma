(function () {
  angular
    .module('irma')
    .factory('UploadModel', Upload);

  function Upload($timeout, alerts, constants, FileUploader, FileItem) {
    // Extending FileItem Object
    angular.extend(FileItem.prototype, {
      getClass,
    });

    // Extending FileUploader Object
    angular.extend(FileUploader.prototype, {
      hasFiles,
      isReady,
      uploadedFiles,
      extractFilesExtId,
    });

    function UploadModel() {
      this.uploader = new FileUploader({
        url: `${constants.baseApi}/files_ext`,
        autoUpload: true,
        alias: 'files',
        formData: [{
          json: JSON.stringify({
            submitter: 'webui',
          }),
        }],
        onSuccessItem,
        onErrorItem,
        onCancelItem,
      });
      return this.uploader;
    }

    return UploadModel;

    // ******************************************************* //
    // Function helpers for Uploader //
    function hasFiles() {
      return this.queue.length > 0;
    }

    function uploadedFiles() {
      return this.queue.filter(item => item.isSuccess);
    }

    function isReady() {
      return !this.isUploading && this.uploadedFiles().length > 0;
    }

    function getClass() {
      if (this.isError || this.isCancel) { return 'danger'; }
      if (this.isUploading) { return 'info'; }
      if (this.isUploaded && this.isSuccess) { return 'success'; }
      return 'warning';
    }

    function onSuccessItem(item, response) {
      angular.extend(item, { file_ext_id: response.result_id });
    }

    function onErrorItem(item) {
      // eslint-disable-next-line no-underscore-dangle
      alerts.add(`<strong>${item.file.name}:</strong> ${item._xhr.statusText || 'Has been filtered'}`, 'danger');
      $timeout(() => {
        item.remove();
      }, 3000);
    }

    function onCancelItem(item) {
      item.remove();
    }

    function extractFilesExtId() {
      const files = [];
      this.queue.forEach((item) => {
        if (item.isUploaded && item.isSuccess && item.file_ext_id) {
          files.push(item.file_ext_id);
        }
      });

      return files;
    }
  }
}());
