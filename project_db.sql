PGDMP                      }         	   projectdb    17.3    17.3     �           0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                           false            �           0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                           false            �           0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                           false            �           1262    16388 	   projectdb    DATABASE     o   CREATE DATABASE projectdb WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'ru-RU';
    DROP DATABASE projectdb;
                     postgres    false            �          0    33260    basket 
   TABLE DATA           8   COPY public.basket (id, bouqet_id, user_id) FROM stdin;
    public               postgres    false    220   �       �          0    41821    bouqets 
   TABLE DATA           o   COPY public.bouqets (id, bouqet_name, bouqet_photo, bouqet_description, bouqet_price, bouqet_busy) FROM stdin;
    public               postgres    false    226   �       �          0    41476    orders 
   TABLE DATA           A   COPY public.orders (id, user_id, bouqets_id, status) FROM stdin;
    public               postgres    false    222   
       �          0    24720    roles 
   TABLE DATA           )   COPY public.roles (id, role) FROM stdin;
    public               postgres    false    218   '       �          0    41804    users 
   TABLE DATA           t   COPY public.users (id, user_id, first_name, username, user_phone_number, email, delivery_address, role) FROM stdin;
    public               postgres    false    224   �       �           0    0    basket_id_seq    SEQUENCE SET     ;   SELECT pg_catalog.setval('public.basket_id_seq', 8, true);
          public               postgres    false    219            �           0    0    bouqets_id_seq    SEQUENCE SET     <   SELECT pg_catalog.setval('public.bouqets_id_seq', 5, true);
          public               postgres    false    225            �           0    0    orders_id_seq    SEQUENCE SET     ;   SELECT pg_catalog.setval('public.orders_id_seq', 7, true);
          public               postgres    false    221            �           0    0    roles_id_seq    SEQUENCE SET     :   SELECT pg_catalog.setval('public.roles_id_seq', 6, true);
          public               postgres    false    217            �           0    0    users_id_seq    SEQUENCE SET     ;   SELECT pg_catalog.setval('public.users_id_seq', 43, true);
          public               postgres    false    223            �   >   x�Mʱ�@����%�ϑ/)O�4Y8�d���m����nW����:9�������      �     x��PIN�@<�_1�,�$ނ��%9����(Q,n/0v�'v<|��GT��� 3ꞩ����'jD<�R��ȶ���+*ޅl�tˇ����:}\�;�cO\�A�e����į��r��S.�A�y�Z�{4Hs�1P�A���~ײ�w������G1��FN��ZO`N��e';za�UR��g��;�g�˒K�jt<��ש���E+Ŕ��ik��b������O�A1Q��,k��z|�옾�Ŝ����Pg�m�$�/�L(R      �      x������ � �      �   N   x�3�0�¾�/�\��7]�p���V�ˈ��/��pa��ƋM\Ɯ&\�raυ�B��R �@%\1z\\\ �a/�      �   �   x�3�4755�0�47�0��V���v]�pa;ｰ��,5�$3S
��XTrq�[ZX�b�����4��Ђl;��M8�,L�L�-�ZR������ʩmnihdnffihn�+M�uH�M���K���0�b�����^lr�_����=... �+�W     