"""Geçmiş veri yükleme (2. aşama).

Her veri seti bölümlere (çeyrek, yıl, ...) ayrılır. Bir bölüm:
  1. kaynaktan indirilir ve ayrıştırılır,
  2. kalite kontrollerinden geçer,
  3. Parquet olarak yazılır ve GitHub Releases'e ("veri-arsivi") yüklenir,
  4. manifest'e (data/manifest/<veri seti>.json, repoda) satır sayısı, sha256, kaynak adresleri,
     çekilme anı ve kontrol sonuçlarıyla kaydedilir.
Böylece hangi verinin nereden, ne zaman geldiği ve hangi testlerden geçtiği her zaman izlenebilir.
"""
