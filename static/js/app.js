// TRIC Academy - Client Interactions & Form Logic

document.addEventListener('DOMContentLoaded', function() {
  initDateOfBirthAndAge();
  initPhotoUploadPreview();
  initSponsorshipToggle();
  initDeclarationAutoFill();
  initMockOtpModal();
  initCompetitionCharts();
});

// 1. Date of Birth, Age Calculation & Single Digit Boxes
function initDateOfBirthAndAge() {
  const dobPicker = document.getElementById('dobPicker');
  const ageDisplay = document.getElementById('ageDisplay');
  const ageInput = document.getElementById('ageInput');
  const minorSection = document.getElementById('minorSection');
  const seniorNotice = document.getElementById('seniorNotice');
  const guardianInput = document.getElementById('guardianInput');
  const occupationInput = document.getElementById('occupationInput');

  const digitBoxes = [
    document.getElementById('d1'), document.getElementById('d2'),
    document.getElementById('m1'), document.getElementById('m2'),
    document.getElementById('y1'), document.getElementById('y2'),
    document.getElementById('y3'), document.getElementById('y4')
  ];

  if (!dobPicker) return;

  function updateFromDate(dateStr) {
    if (!dateStr) return;
    const parts = dateStr.split('-');
    if (parts.length !== 3) return;

    const y = parts[0];
    const m = parts[1];
    const d = parts[2];

    // Populate digit boxes DD MM YYYY
    if (digitBoxes[0] && d.length === 2) {
      digitBoxes[0].textContent = d[0];
      digitBoxes[1].textContent = d[1];
    }
    if (digitBoxes[2] && m.length === 2) {
      digitBoxes[2].textContent = m[0];
      digitBoxes[3].textContent = m[1];
    }
    if (digitBoxes[4] && y.length === 4) {
      digitBoxes[4].textContent = y[0];
      digitBoxes[5].textContent = y[1];
      digitBoxes[6].textContent = y[2];
      digitBoxes[7].textContent = y[3];
    }

    // Calculate age
    const birthDate = new Date(y, parseInt(m, 10) - 1, d);
    const today = new Date();
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }

    if (age >= 0 && age < 120) {
      if (ageDisplay) ageDisplay.textContent = age;
      if (ageInput) ageInput.value = age;

      // Minor rules (< 18)
      if (minorSection) {
        if (age < 18) {
          minorSection.style.display = 'flex';
          if (guardianInput) guardianInput.required = true;
          if (occupationInput) occupationInput.required = true;
        } else {
          minorSection.style.display = 'none';
          if (guardianInput) guardianInput.required = false;
          if (occupationInput) occupationInput.required = false;
        }
      }

      // Senior rules (> 50)
      if (seniorNotice) {
        seniorNotice.style.display = age > 50 ? 'block' : 'none';
      }
    }
  }

  dobPicker.addEventListener('change', function(e) {
    updateFromDate(e.target.value);
  });

  // Initial calculation if editing existing or prefilled
  if (dobPicker.value) {
    updateFromDate(dobPicker.value);
  }
}

// 2. Photo Upload Preview
function initPhotoUploadPreview() {
  const photoInput = document.getElementById('photoInput');
  const photoContainer = document.getElementById('photoContainer');
  const photoPreview = document.getElementById('photoPreview');
  const photoPlaceholder = document.getElementById('photoPlaceholder');

  if (!photoInput || !photoContainer) return;

  photoContainer.addEventListener('click', function() {
    photoInput.click();
  });

  photoInput.addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
      // Validate file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        alert('Passport photo size must be under 5MB.');
        photoInput.value = '';
        return;
      }
      const reader = new FileReader();
      reader.onload = function(evt) {
        if (photoPreview) {
          photoPreview.src = evt.target.result;
          photoPreview.style.display = 'block';
        }
        if (photoPlaceholder) {
          photoPlaceholder.style.display = 'none';
        }
      };
      reader.readAsDataURL(file);
    }
  });
}

// 3. Department Sponsorship Toggle
function initSponsorshipToggle() {
  const sponsoredYes = document.getElementById('sponsoredYes');
  const sponsoredNo = document.getElementById('sponsoredNo');
  const sponsorUploadWrap = document.getElementById('sponsorUploadWrap');
  const sponsorFileInput = document.getElementById('sponsorFileInput');

  if (!sponsoredYes || !sponsorUploadWrap) return;

  function toggleSponsor() {
    if (sponsoredYes.checked) {
      sponsorUploadWrap.style.display = 'block';
      if (sponsorFileInput) sponsorFileInput.required = true;
    } else {
      sponsorUploadWrap.style.display = 'none';
      if (sponsorFileInput) sponsorFileInput.required = false;
    }
  }

  sponsoredYes.addEventListener('change', toggleSponsor);
  if (sponsoredNo) sponsoredNo.addEventListener('change', toggleSponsor);
  toggleSponsor();
}

// 4. Auto-fill Declaration Name and Signature
function initDeclarationAutoFill() {
  const applicantNameInput = document.getElementById('applicantNameInput');
  const declarationNameSpan = document.getElementById('declarationNameSpan');
  const signatureInput = document.getElementById('signatureInput');

  if (!applicantNameInput) return;

  if (signatureInput) {
    signatureInput.addEventListener('input', function() {
      signatureInput.dataset.manuallyEdited = 'true';
    });
  }

  applicantNameInput.addEventListener('input', function(e) {
    const name = e.target.value.trim();
    if (declarationNameSpan) {
      declarationNameSpan.textContent = name || '____________________';
    }
    if (signatureInput && (!signatureInput.dataset.manuallyEdited || !signatureInput.value.trim())) {
      signatureInput.value = name;
    }
  });
}

// 5. Robust Public Form Validation and Simulated Mock OTP Flow
function initMockOtpModal() {
  const applicationForm = document.getElementById('applicationForm');
  const submitFormBtn = document.getElementById('submitFormBtn');
  const otpModal = document.getElementById('otpModal');
  const otpCodeDisplay = document.getElementById('otpCodeDisplay');
  const otpInputField = document.getElementById('otpInputField');
  const autoFillOtpBtn = document.getElementById('autoFillOtpBtn');
  const verifyOtpBtn = document.getElementById('verifyOtpBtn');
  const otpErrorMsg = document.getElementById('otpErrorMsg');

  if (!applicationForm || window._applicationFormScriptLoaded) return;

  const isPublicSignup = applicationForm.getAttribute('data-is-public') === 'true';

  function showValidationError(msg, targetInput) {
    const errBanner = document.getElementById('formValidationError');
    const errMsg = document.getElementById('formValidationMsg');
    if (errBanner && errMsg) {
      errMsg.textContent = msg;
      errBanner.style.display = 'block';
      errBanner.scrollIntoView({ behavior: 'smooth', block: 'center' });
    } else {
      alert(msg);
    }
    if (targetInput) {
      try {
        targetInput.focus();
        targetInput.style.outline = '2px solid #EF4444';
        targetInput.style.borderColor = '#EF4444';
        setTimeout(() => {
          targetInput.style.outline = '';
          targetInput.style.borderColor = '';
        }, 3500);
      } catch (_) {}
    }
  }

  function validatePublicForm() {
    // 1. Applicant Name
    const nameInput = document.getElementById('applicantNameInput');
    if (!nameInput || !nameInput.value.trim()) {
      showValidationError('Please enter the Name of the Applicant.', nameInput);
      return false;
    }

    // 2. Address
    const addressInput = document.getElementById('addressInput');
    if (!addressInput || !addressInput.value.trim()) {
      showValidationError('Please enter your residential Address.', addressInput);
      return false;
    }

    // 3. Pincode
    const pincodeInput = document.querySelector('input[name="pincode"]');
    if (!pincodeInput || !pincodeInput.value.trim()) {
      showValidationError('Please enter your Pin Code (e.g. 641652).', pincodeInput);
      return false;
    }

    // 4. Contact No
    const phoneInput = document.getElementById('phoneInput');
    if (!phoneInput || !phoneInput.value.trim()) {
      showValidationError('Please enter your 10-digit mobile Contact Number.', phoneInput);
      return false;
    }
    const cleanPhone = phoneInput.value.trim().replace(/\D/g, '');
    if (cleanPhone.length < 10) {
      showValidationError('Contact Number must be a valid 10-digit phone number.', phoneInput);
      return false;
    }

    // 5. Email ID
    const emailInput = document.getElementById('emailInput');
    if (!emailInput || !emailInput.value.trim() || !emailInput.value.includes('@')) {
      showValidationError('Please enter a valid Email ID.', emailInput);
      return false;
    }

    // 6. Date of Birth
    const dobPicker = document.getElementById('dobPicker');
    if (!dobPicker || !dobPicker.value) {
      showValidationError('Please select your Date of Birth.', dobPicker);
      return false;
    }

    // 7. Minor validations (< 18 yrs)
    const ageVal = parseInt(document.getElementById('ageInput')?.value || '99', 10);
    if (!isNaN(ageVal) && ageVal < 18) {
      const guardianInput = document.getElementById('guardianInput');
      const occupationInput = document.getElementById('occupationInput');
      if (!guardianInput || !guardianInput.value.trim()) {
        showValidationError('Parent / Guardian Name is mandatory for minor applicants (under 18).', guardianInput);
        return false;
      }
      if (!occupationInput || !occupationInput.value.trim()) {
        showValidationError('Parent / Guardian Occupation is mandatory for minor applicants.', occupationInput);
        return false;
      }
    }

    // 8. Password for member login
    const passwordInput = document.getElementById('passwordInput');
    if (passwordInput && passwordInput.value.length < 6) {
      showValidationError('Please create an account password with at least 6 characters.', passwordInput);
      return false;
    }

    // 9. Health Declaration
    const healthDeclared = document.getElementById('healthDeclared');
    if (healthDeclared && !healthDeclared.checked) {
      showValidationError('Please confirm the Health Declaration checkbox.', healthDeclared);
      return false;
    }

    // 10. Mandatory 32 Rules & Regulations confirmation
    const rulesAgreed = document.getElementById('rulesAgreed');
    if (rulesAgreed && !rulesAgreed.checked) {
      showValidationError('Mandatory Requirement: You must read and accept all 32 Rules & Regulations.');
      if (typeof openRulesModal === 'function') {
        openRulesModal();
      }
      return false;
    }

    // 11. Signature Name
    const signatureInput = document.getElementById('signatureInput');
    if (signatureInput && !signatureInput.value.trim()) {
      signatureInput.value = nameInput.value.trim();
    }

    // Hide any previous validation banner
    const errBanner = document.getElementById('formValidationError');
    if (errBanner) errBanner.style.display = 'none';

    return true;
  }

  function submitFormDirectly() {
    const btn = document.getElementById('submitFormBtn');
    if (btn) {
      btn.disabled = true;
      btn.textContent = 'Submitting Application...';
    }
    HTMLFormElement.prototype.submit.call(applicationForm);
  }

  function handleFormSubmission(e) {
    if (e && e.preventDefault) e.preventDefault();

    if (!isPublicSignup) {
      // Admin mode: direct submission
      HTMLFormElement.prototype.submit.call(applicationForm);
      return;
    }

    if (!validatePublicForm()) {
      return;
    }

    const phoneVerified = document.getElementById('phoneVerifiedFlag');
    if (phoneVerified) {
      phoneVerified.value = '1';
    }
    const mockOtpField = document.getElementById('mockOtpField');
    if (mockOtpField) {
      mockOtpField.value = '123456';
    }

    submitFormDirectly();
  }

  // Hook submit button click
  if (submitFormBtn) {
    submitFormBtn.addEventListener('click', handleFormSubmission);
  }

  // Hook native form submit
  applicationForm.addEventListener('submit', handleFormSubmission);

  // Hook Auto-Fill OTP button
  if (autoFillOtpBtn) {
    autoFillOtpBtn.addEventListener('click', function() {
      if (otpInputField && window._currentMockOtp) {
        otpInputField.value = window._currentMockOtp;
      }
    });
  }

  // Hook OTP verification confirmation
  if (verifyOtpBtn) {
    verifyOtpBtn.addEventListener('click', function() {
      const entered = otpInputField ? otpInputField.value.trim() : '';
      if (entered === window._currentMockOtp || !entered || entered === otpCodeDisplay?.textContent) {
        const phoneVerified = document.getElementById('phoneVerifiedFlag');
        const mockOtpField = document.getElementById('mockOtpField');
        if (phoneVerified) phoneVerified.value = '1';
        if (mockOtpField) mockOtpField.value = window._currentMockOtp || entered;
        if (otpModal) otpModal.style.display = 'none';
        submitFormDirectly();
      } else {
        if (otpErrorMsg) {
          otpErrorMsg.style.display = 'block';
          otpErrorMsg.textContent = 'Incorrect OTP code. Enter ' + window._currentMockOtp;
        }
      }
    });
  }
}

// 6. Competition Charts using Chart.js
function initCompetitionCharts() {
  const chartCanvas = document.getElementById('swimmerProgressChart');
  if (!chartCanvas || typeof Chart === 'undefined') return;

  const rawData = chartCanvas.getAttribute('data-records');
  if (!rawData) return;

  try {
    const records = JSON.parse(rawData);
    if (!records || records.length === 0) return;

    // Group by stroke
    const strokes = {};
    records.forEach(r => {
      const label = `${r.distance} ${r.stroke}`;
      if (!strokes[label]) strokes[label] = [];
      strokes[label].push({
        x: r.meet_date,
        y: r.time_seconds,
        display: r.time_display,
        meet: r.meet_name
      });
    });

    const colors = ['#0284C7', '#1F8A8A', '#D97706', '#9333EA', '#DC2626'];
    let cIdx = 0;

    const datasets = Object.keys(strokes).map(label => {
      const color = colors[cIdx % colors.length];
      cIdx++;
      return {
        label: label.toUpperCase(),
        data: strokes[label].map(d => ({ x: d.x, y: d.y })),
        borderColor: color,
        backgroundColor: color,
        borderWidth: 2,
        tension: 0.2,
        pointRadius: 5,
        pointHoverRadius: 7
      };
    });

    new Chart(chartCanvas, {
      type: 'line',
      data: { datasets: datasets },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            title: { display: true, text: 'Competition Meet Date' }
          },
          y: {
            title: { display: true, text: 'Race Time (Seconds)' },
            beginAtZero: false
          }
        },
        plugins: {
          legend: { position: 'top' },
          tooltip: {
            callbacks: {
              label: function(context) {
                const sec = context.parsed.y;
                const mins = Math.floor(sec / 60);
                const rem = (sec % 60).toFixed(2);
                const disp = mins > 0 ? `${mins}:${rem.padStart(5, '0')}` : `${rem}s`;
                return `${context.dataset.label}: ${disp}`;
              }
            }
          }
        }
      }
    });
  } catch (err) {
    console.error('Failed to parse competition chart data', err);
  }
}
