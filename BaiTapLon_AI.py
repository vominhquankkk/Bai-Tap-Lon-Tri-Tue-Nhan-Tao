import heapq
import copy

class SapXepVong:
    def __init__(self, trang_thai_ban_dau):
        self.trang_thai_ban_dau = trang_thai_ban_dau
        self.trang_thai_muc_tieu = self.lay_trang_thai_muc_tieu(trang_thai_ban_dau)

    def lay_trang_thai_muc_tieu(self, trang_thai):
        return sorted(trang_thai, key=lambda x: (len(set(x)), x))
    
    def la_trang_thai_muc_tieu(self, trang_thai):
        return trang_thai == self.trang_thai_muc_tieu

    def lay_lan_can(self, trang_thai):
        lan_can = []
        for i in range(len(trang_thai)):
            if not trang_thai[i]:
                continue
            
            for j in range(len(trang_thai)):
                if i != j and (not trang_thai[j] or trang_thai[j][-1] == trang_thai[i][-1]):
                    trang_thai_moi = copy.deepcopy(trang_thai)
                    vong_dang_di_chuyen = []
                    
                    while trang_thai_moi[i] and (not trang_thai_moi[j] or trang_thai_moi[i][-1] == trang_thai_moi[j][-1]):
                        vong_dang_di_chuyen.append(trang_thai_moi[i].pop())
                        
                    trang_thai_moi[j].extend(reversed(vong_dang_di_chuyen))
                    lan_can.append((trang_thai_moi, (i, j)))
        
        return lan_can
    
    def heuristic(self, trang_thai):
        sai_vi_tri = sum(1 for i in range(len(trang_thai)) if trang_thai[i] and len(set(trang_thai[i])) > 1)
        return sai_vi_tri

    def giai(self):
        hang_doi_uu_tien = []
        heapq.heappush(hang_doi_uu_tien, (0, self.trang_thai_ban_dau, []))
        da_tham = set()
        
        while hang_doi_uu_tien:
            chi_phi, trang_thai_hien_tai, buoc_di = heapq.heappop(hang_doi_uu_tien)
            trang_thai_tuple = tuple(tuple(cot) for cot in trang_thai_hien_tai)
            
            if trang_thai_tuple in da_tham:
                continue
            da_tham.add(trang_thai_tuple)
            
            if self.la_trang_thai_muc_tieu(trang_thai_hien_tai):
                return buoc_di
            
            for lan_can, di_chuyen in self.lay_lan_can(trang_thai_hien_tai):
                chi_phi_moi = chi_phi + 1 + self.heuristic(lan_can)
                heapq.heappush(hang_doi_uu_tien, (chi_phi_moi, lan_can, buoc_di + [di_chuyen]))
        
        return None

if __name__ == "__main__":
    trang_thai_ban_dau = [
        ["đỏ", "xanh lá", "xanh dương", "vàng"],
        ["đỏ", "xanh dương", "xanh lá", "vàng"],
        ["vàng", "xanh dương", "đỏ", "xanh lá"],
        ["xanh lá", "vàng", "đỏ", "xanh dương"],
        [], []
    ]
    
    sap_xep = SapXepVong(trang_thai_ban_dau)
    loi_giai = sap_xep.giai()
    
    if loi_giai:
        print("Đã tìm thấy lời giải:")
        for buoc, di_chuyen in enumerate(loi_giai, 1):
            print(f"Bước {buoc}: Chuyển từ cột {di_chuyen[0]} sang cột {di_chuyen[1]}")
    else:
        print("Không tìm thấy lời giải.")
