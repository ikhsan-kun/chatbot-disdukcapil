// ==========================================
// SHARED INTERACTIVE CONTROLLER (NON-CHATBOT)
// ==========================================


// ==========================
// HAMBURGER MENU
// ==========================
document.addEventListener("DOMContentLoaded", function () {

    const hamburger = document.getElementById("hamburger");
    const navMenu = document.querySelector(".nav-menu");

    if (hamburger) {
        hamburger.addEventListener("click", function () {
            navMenu.classList.toggle("active");
        });
    }

});

// popup chatbot removed - handled by static/chatbot.js



// pengajuan
function toggleForm(id) {
    const form = document.getElementById(id);

    if (form.style.display === "block") {
        form.style.display = "none";
    } else {
        form.style.display = "block";
    }
}

// dropdown nama
function toggleDropdown() {
    const menu = document.getElementById("dropdownMenu");
    menu.style.display = menu.style.display === "flex" ? "none" : "flex";
}

// klik luar = tutup
window.onclick = function(e) {
    if (!e.target.matches('.user-btn')) {
        const menu = document.getElementById("dropdownMenu");
        if (menu) menu.style.display = "none";
    }
}

// tampilan riwayat pengajuan
function openDetail(button)
{
    const item =
        JSON.parse(button.dataset.item);

    // Mapping nilai raw dropdown ke label terbaca manusia
    const DETAIL_LABEL_MAP = {
        // KK
        'anggota'       : 'Perubahan Anggota Keluarga',
        'alamat'        : 'Perubahan Domisili/Alamat',
        'lainnya'       : 'Perubahan Lainnya (Hilang/Rusak/Lainnya)',
        // Pendidikan
        'tidak_sekolah' : 'Tidak/Belum Sekolah',
        'belum_tamat_sd': 'Belum Tamat SD/Sederajat',
        'tamat_sd'      : 'Tamat SD/Sederajat',
        'sltp'          : 'SLTP/Sederajat',
        'slta'          : 'SLTA/Sederajat',
        'diploma_1_2'   : 'Diploma I/II',
        'diploma_3'     : 'Akademi/Diploma III/Sarjana Muda',
        's1'            : 'Diploma IV/Strata I',
        's2'            : 'Strata II'
    };

    document.getElementById("modalDetail").style.display =
        "flex";

    // =========================
    // DETAIL DATA
    // =========================
    document.getElementById("dLayanan").innerText =
        item.jenis_layanan;

document.getElementById("dDetailPengajuan").innerText =
    DETAIL_LABEL_MAP[item.detail_pengajuan] || item.detail_pengajuan || "-";

    document.getElementById("dNik").innerText =
        item.nik;

    // nama lengkap
document.getElementById("dNamaLengkap").innerText =
    item.nama || "-";

    // pendidikan lama
    const pendidikanLama =
        document.getElementById("dPendidikanLama");

    if (pendidikanLama)
    {
        pendidikanLama.innerText =
            item.pendidikan_lama || "-";
    }

    document.getElementById("dTanggal").innerText =
        item.tanggal_pengajuan;

    document.getElementById("modalStatus").innerText =
        item.status;

        // =========================
// TAMPIL / SEMBUNYIKAN
// PENDIDIKAN LAMA
// =========================

const boxPendidikanLama =
    document.getElementById("boxPendidikanLama");

if (item.jenis_layanan === "Perubahan Status Pendidikan")
{
    boxPendidikanLama.style.display = "block";
}
else
{
    boxPendidikanLama.style.display = "none";
}

// =========================
// DETAIL PENGAJUAN
// =========================

const boxDetailPengajuan =
    document.getElementById("boxDetailPengajuan");

if (item.detail_pengajuan)
{
    boxDetailPengajuan.style.display = "block";

    // Update label sesuai jenis layanan
    const labelDetail = document.getElementById("labelDetailPengajuan");
    if (labelDetail) {
        labelDetail.innerText = (item.jenis_layanan === "Perubahan Status Pendidikan")
            ? "Pendidikan Terbaru"
            : "Jenis Pengajuan KK";
    }
}
else
{
    boxDetailPengajuan.style.display = "none";
}

    // =========================
    // DETAIL KARTU KELUARGA (KK)
    // =========================
    const boxKkDetails = document.getElementById("boxKkDetails");
    if (boxKkDetails) {
        if (item.jenis_layanan === "Cetak Ulang KK") {
            boxKkDetails.style.display = "block";
            document.getElementById("dNoKk").innerText = item.no_kk || "-";
            document.getElementById("dAlamat").innerText = item.alamat || "-";
            document.getElementById("dProvinsi").innerText = item.provinsi || "-";
            document.getElementById("dKabupaten").innerText = item.kabupaten || "-";
            document.getElementById("dKecamatan").innerText = item.kecamatan || "-";
            document.getElementById("dDesa").innerText = item.desa || "-";
        } else {
            boxKkDetails.style.display = "none";
        }
    }

    // =========================
    // DOKUMEN USER
    // =========================
    let htmlDokumen = "";

    if (item.dokumen && item.dokumen.length > 0)
    {
        item.dokumen.forEach(file => {

            htmlDokumen += `
                <a
                    href="/static/uploads/${file.nama_file}"
                    target="_blank"
                    class="file-btn"
                    style="display:block; margin-bottom:10px;"
                >
                    📄 ${file.nama_file}
                </a>
            `;
        });

        document.getElementById("dokumenUserList")
            .innerHTML = htmlDokumen;

        document.getElementById("boxUser")
            .style.display = "block";

    }
    else
    {
        document.getElementById("boxUser")
            .style.display = "none";
    }

    // =========================
    // CATATAN USER
    // =========================
    document.getElementById("catatanUser").innerText =
        item.catatan_user || "-";

    // =========================
    // CATATAN ADMIN
    // =========================
    document.getElementById("catatanAdmin").innerText =
        item.catatan_admin || "Belum ada balasan admin";

    document.getElementById("boxCatatan")
        .style.display = "block";

    // =========================
    // FILE ADMIN
    // =========================
    const linkAdmin =
        document.getElementById("linkAdmin");

    document.getElementById("boxAdmin")
        .style.display = "block";

    if (
        item.file_balasan &&
        item.file_balasan !== "None" &&
        item.file_balasan !== ""
    )
    {
        // ADA FILE
        linkAdmin.href =
            "/static/uploads/" + item.file_balasan;

        linkAdmin.className = "file-btn btn-active-admin";
        linkAdmin.style.pointerEvents = "";
        linkAdmin.style.opacity = "";
        linkAdmin.style.background = "";

        linkAdmin.innerText =
            "📄 Lihat Dokumen";

    }
    else
    {
        // TIDAK ADA FILE
        linkAdmin.href = "#";

        linkAdmin.className = "file-btn btn-inactive-admin";
        linkAdmin.style.pointerEvents = "";
        linkAdmin.style.opacity = "";
        linkAdmin.style.background = "";

        linkAdmin.innerText =
            "Belum Ada Dokumen";
    }

    // =========================
    // INFO STATUS
    // =========================
    let info = "";

    if (item.status === "Menunggu Verifikasi")
    {
        info =
            "Pengajuan Anda sedang menunggu verifikasi admin.";

    }
    else if (item.status === "Diproses")
    {
        info =
            "Pengajuan Anda sedang diproses oleh admin.";

    }
    else if (item.status === "Disetujui")
    {
        info =
            "Pengajuan Anda telah disetujui.";

    }
    else if (item.status === "Ditolak")
    {
        info =
            "Pengajuan Anda ditolak.";
    }
    else if (item.status === "Selesai")
    {
        info =
            "✅ Pengajuan Anda telah selesai diproses.";
    }

    document.getElementById("infoStatus").innerText =
        info;
}

// close modal
function closeDetail() {

    document.getElementById("modalDetail").style.display =
        "none";

    document.getElementById("linkAdmin").href = "#";

    // reset semua box
    document.getElementById("boxUser").style.display =
        "none";

    document.getElementById("boxCatatan").style.display =
        "none";

    const boxKkDetails = document.getElementById("boxKkDetails");
    if (boxKkDetails) {
        boxKkDetails.style.display = "none";
    }
}

// admin proses
function openProsesModal(id) {
    const modal = document.getElementById("modalProses");
    if (!modal) return;  // Fix Bug #11: null check

    modal.style.display = "flex";

    // set form action dinamis
    const form = document.getElementById("formProses");
    if (form) form.action = "/admin/proses/" + id;
}

function closeProsesModal() {
    const modal = document.getElementById("modalProses");
    if (!modal) return;  // Fix Bug #11: null check

    modal.style.display = "none";
}


// show password
function togglePassword() {
    const input = document.getElementById("password");
    const iconShow = document.getElementById("iconShow");
    const iconHide = document.getElementById("iconHide");

    if (input.type === "password") {
        input.type = "text";
        iconShow.style.display = "none";
        iconHide.style.display = "block";
    } else {
        input.type = "password";
        iconShow.style.display = "block";
        iconHide.style.display = "none";
    }
}

// show confirm password
function toggleConfirmPassword() {
    const input = document.getElementById("confirm_password");
    const iconShow = document.getElementById("iconShowConfirm");
    const iconHide = document.getElementById("iconHideConfirm");

    if (input.type === "password") {
        input.type = "text";
        iconShow.style.display = "none";
        iconHide.style.display = "block";
    } else {
        input.type = "password";
        iconShow.style.display = "block";
        iconHide.style.display = "none";
    }
}

// ==========================================================================
// LIHAT SELENGKAPNYA PERSYARATAN
// ==========================================================================
document.addEventListener("DOMContentLoaded", function() {
    const lists = document.querySelectorAll('.syarat-list');
    lists.forEach(function(list) {
        const items = list.querySelectorAll('p');
        // Hanya jika persyaratan lebih dari 3
        if (items.length > 3) {
            // Sembunyikan item index >= 3
            for (let i = 3; i < items.length; i++) {
                items[i].style.display = 'none';
            }
            
            // Buat tombol "Lihat Selengkapnya"
            const btn = document.createElement('button');
            btn.className = 'btn-selengkapnya';
            btn.innerHTML = 'Lihat Selengkapnya &darr;';
            
            btn.addEventListener('click', function() {
                const isExpanded = btn.innerHTML.includes('Sembunyikan');
                for (let i = 3; i < items.length; i++) {
                    items[i].style.display = isExpanded ? 'none' : 'block';
                }
                btn.innerHTML = isExpanded ? 'Lihat Selengkapnya &darr;' : 'Sembunyikan &uarr;';
            });
            
            // Masukkan tombol setelah list persyaratan
            list.parentNode.appendChild(btn);
        }
    });
});

// ==========================================
// TOAST NOTIFICATION SYSTEM
// ==========================================
function showToast(message, type = 'error') {
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }
    
    const toast = document.createElement('div');
    toast.className = `toast-notification ${type}`;
    
    let icon = '❌';
    if (type === 'success') icon = '✅';
    if (type === 'warning') icon = '⚠️';
    
    toast.innerHTML = `
        <div class="toast-icon">${icon}</div>
        <div class="toast-content">${message}</div>
        <button class="toast-close" onclick="this.parentElement.remove()">×</button>
    `;
    
    container.appendChild(toast);
    
    // Trigger animation
    setTimeout(() => {
        toast.classList.add('show');
    }, 10);
    
    // Auto dismiss after 4 seconds
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, 4000);
}