# SimpleLattice

a small blender 2.9 addon to make working with lattices simpler.

Basically just select objects/vertices and run>SimpleLattice. This will add a lattice object, creates modifiers and vertex groups. 
You can choose the alignment of the lattice, the number of control points and the interplation type.

It also does auto cleanup in the back, but only on modifiers & vertex groups with "SimpleLattice" in the name.

How to use:

  1. RMB on selected objects or elements - Create Lattice.
  2. RMB on lattice object - Apply/Remove or tweak strength.

Examples:

  1. Object mode - multiple objects

https://user-images.githubusercontent.com/87300864/129005850-5dd55a01-a4b6-4563-a1a3-bb604aecedec.mp4

  2. Edit mode - multiple objects

https://user-images.githubusercontent.com/87300864/129006117-9be021ac-ddcc-401c-b9ce-5fc3e12b24bc.mp4

  3. Single object editing

https://user-images.githubusercontent.com/87300864/129006206-5f0216a5-43be-4c3d-bb6c-3915fed2c579.mp4

-----------------------------------------------------------------------------------------------------

## Update 0.1.1
1. Added new orientation - Normal. It simply create orientation from selection and align Lattice.
2. Added possibility to change Lattice resolution in RMB menu, when Lattice is selected.

https://user-images.githubusercontent.com/87300864/130314258-247fdae1-cb4c-4a04-9325-b5ede65cbcb1.mp4

https://user-images.githubusercontent.com/87300864/130314393-aa7842e3-978c-4d40-aa35-995bc98be90c.mp4

-----------------------------------------------------------------------------------------------------

## Update 0.1.2
1. Little UI tweaks.
2. Added Addon preferences - where you can define default values for adding Lattice.

![SimpleLattice_0 1 2](https://user-images.githubusercontent.com/87300864/130365642-55e18d9a-a52f-4315-b31d-193001bab57c.png)
![SimpleLattice_AddonPreferences_0 1 2](https://user-images.githubusercontent.com/87300864/130365643-890445a6-7de0-4759-b936-4e8d573a21de.png)

------------------------------------------------------------------------------------------------------

## Update 0.1.3
1. Added option "Ignore Modifiers". For cases where you need to modify only original object.
![update 0 1 3](https://user-images.githubusercontent.com/87300864/179476670-bf75c4bb-6f91-4d0e-a618-fe233f775600.png)
2. Added Addon preference for "Ignore Modifiers".
![update 0 1 3 prefs](https://user-images.githubusercontent.com/87300864/179476954-3f40aa49-9e0b-40e0-ab50-7fe92b8af7c5.png)

------------------------------------------------------------------------------------------------------

## Update 0.1.4
1. Fix for "Flat" surfaces (was impossible to manipulate lattice points)
2. Fix for Grease Pencil objects (can create lattice for object, but not for gpencil selection points)

------------------------------------------------------------------------------------------------------

## Update 0.1.5
1. Minor UI changes for search operator

![Search_in_Object_Mode](https://user-images.githubusercontent.com/87300864/210093381-b38bd70c-69db-45cd-accf-b8fb5c9b0bd4.png)
![Search_in_Edit_Mode](https://user-images.githubusercontent.com/87300864/210093394-e7c943f7-99aa-441a-81d9-64f50f63eb44.png)

2. Added menu entry to Object and Mesh

![Menu_Object](https://user-images.githubusercontent.com/87300864/210093566-7f73b3f5-13cd-466e-893c-37ca9155b806.png)
![Menu_Mesh](https://user-images.githubusercontent.com/87300864/210093573-fa226c2c-81a5-489f-ac4a-fc1042ab03c7.png)

3. Fix for instanced object/s. Now, before applying the lattice, it makes a single user and then applies the lattice.

------------------------------------------------------------------------------------------------------

## Update 0.1.6
1. More accurate bbox calculation for MESH objects if object have custom rotation
![Before_After_0_1_6](https://user-images.githubusercontent.com/87300864/229338682-d7e29066-8159-46bc-8be6-df34152bb195.png)

2. New feature to tweak angles for created lattice object
![Tweak_Angles_0_1_6](https://user-images.githubusercontent.com/87300864/229339007-48fbc619-454b-4c70-b699-8a2dfb524c95.png)

https://user-images.githubusercontent.com/87300864/229339025-baf61493-59dc-4dc4-878e-4fc9bcb01a9e.mp4
